from typing import Callable
import argparse
import re
import sys
import html
import os.path
from datetime import datetime

from pathlib import Path
from xml.etree import ElementTree as ET

import feedparser


def nettoyage(texte):
    texte_net = re.sub(r"<!\[CDATA\[(.*?)\]\]>", "\\1", texte, flags=re.DOTALL)
    texte_net = html.unescape(texte_net)
    texte_net = re.sub("<.+?>", "", texte_net)
    texte_net = re.sub("\n+", " ", texte_net)
    texte_net = texte_net.strip()
    return texte_net


def rss_reader_re(filename: str | Path) -> list[dict]:
    articles = []
    name = Path(filename).name
    global_categories = set()

    with open(filename, "r") as input_rss:
        texte = input_rss.read()

        if (match := re.search("<channel>.+?<item>", texte, flags=re.DOTALL)) is not None:
            header = match.group(0)
            for submatch in re.finditer("<category.*>(.+?)</category>", header):
                global_categories.add(submatch.group(1))

        for match in re.finditer(r"<item>.*?</item>", texte, flags=re.DOTALL):
            item = match.group(0)

            title = re.search(r"<title.*?>(.+?)</title>", item).group(1)
            title = nettoyage(title)
            description = re.search(r"<description.*?>(.*?)</description>", item, flags=re.DOTALL).group(1)
            description = nettoyage(description)

            local_categories = global_categories.copy()
            for category in re.finditer(r"<category.*?>(.+?)</category>", item):
                local_categories.add(category.group(1))

            dataid = re.search(r"<guid.*?>(.+?)</guid>", item).group(1)

            pubdate_element = re.search(r"<pubDate.*?>(.+?)</pubDate>", item)
            if pubdate_element is not None:
                pubdate = nettoyage(pubdate_element.group(1))
            else:
                pubdate = ""

            article = {
                "id": dataid,
                "source": name,
                "title": title,
                "description": description,
                "date": pubdate,
                "categories": sorted(local_categories),
            }
            articles.append(article)

    return articles


def rss_reader_etree(filename: str | Path) -> list[dict]:
    name = Path(filename).name

    if name.lower() in ("flux.xml", "flux rss.xml"): # erreur de parsing
        return []

    try:
        root = ET.parse(filename)
    except ET.ParseError:
        return []

    articles = []
    global_categories = set(element.text.strip() for element in root.iterfind("./channel/category"))

    for item in root.iterfind(".//item"):
        dataid = item.find("guid").text

        # particularité etree : ne pas vérifier la valeur avec juste if, mais bien avec "is None" ou "is not None"
        # doc : https://docs.python.org/3/library/xml.etree.elementtree.html#xml.etree.ElementTree.Element.remove
        title_element = item.find("title")
        if title_element is not None:
            title = title_element.text or ""
        else:
            title = ""
        title = nettoyage(title)

        description_element = item.find("description")
        if description_element is not None:
            description = description_element.text or ""
        else:
            description = ""
        description = nettoyage(description)

        pubdate_element = item.find("pubDate")
        if pubdate_element is None:
            pubdate_element = item.find("lastpublished")
        if pubdate_element is not None:
            pubdate = pubdate_element.text
        else:
            pubdate = None
        if pubdate is not None:
            pubdate = nettoyage(pubdate)

        local_categories = global_categories.copy()
        for category_element in item.iterfind("category"):
            local_categories.add(category_element.text)

        article = {
            "id": dataid,
            "source": name,
            "title": title,
            "description": description,
            "date": pubdate,
            "categories": sorted(local_categories),
        }
        articles.append(article)

    return articles


def rss_reader_feedparser(filename: str | Path) -> list[dict]:
    name = Path(filename).name
    feed = feedparser.parse(filename)
    articles = []
    global_categories = set([item["term"] for item in feed["feed"].get("tags", [])])

    for item in feed["entries"]:
        pubdate = item.get("published")
        if not pubdate:
            pubdate = item.get("lastpublicationdate")

        categories = global_categories | set(t["term"] for t in item.get("tags", []))

        article = {
            "id": item.id,
            "source": name,
            "title": nettoyage(item.title),
            "description": nettoyage(item.get("description")),
            "date": pubdate,
            "categories": sorted(categories),
        }
        articles.append(article)

    return articles


def walk_os(path: str) -> list[str]:
    return []


def walk_pathlib(path: str) -> list[str]:
    filepath = Path(path)

    if filepath.is_file():
        if filepath.suffix == ".xml":
            return [path]
        else:
            return []

    files = sorted(filepath.iterdir())

    if len(files) == 0:
        return []

    result = []
    for file in files:
        if file.is_file() and file.suffix == ".xml":
            result.append(str(file))
        elif file.is_dir():
            result.extend(str(file) for file in walk_pathlib(file))
    return result


def walk_glob(path: str) -> list[str]:
    return sorted(str(filepath) for filepath in Path(path).glob("**/*.xml"))


def filtre_vrai(article: dict) -> bool:
    return True


def create_filter_start_date(start: str) -> Callable[[dict], bool]:
    start_date = datetime.strptime(start, "%d/%m/%y")
    def filtre(a: dict) -> bool:
        try:
            d = datetime.strptime(" ".join(a['date'].split()[:4]), '%a, %d %b %Y')
        except ValueError:
            try:
                d = datetime.strptime(" ".join(a['date'].split()[:4]), '%a, %d %b %y')
            except ValueError:
                # date non valide, on écarte l'article
                return False
        return start_date <= d
    return filtre


def create_filter_categories(categories: list[str]) -> Callable[[dict], bool]:
    cat_set = set(categories)
    def filtre(a: dict) -> bool:
        return len(cat_set.intersection(a['categories'])) > 0
    return filtre


def build_filters(args: argparse.Namespace) -> list[Callable[[dict], bool]]:
    filtres = []
    if args.start:
        f = create_filter_start_date(args.start)
        filtres.append(f)
    if len(args.categories) > 0:
        f = create_filter_categories(args.categories)
        filtres.append(f)
    return filtres


def filtrage(filtres: list[Callable[[dict], bool]], articles: list[dict]) -> list[dict]:
    resultat = []
    for a in articles:
        if all([f(a) for f in filtres]):
            resultat.append(a)
    return resultat


def main():
    parser = argparse.ArgumentParser(description="foobar")

    parser.add_argument("rss_feed")
    parser.add_argument("-w", "--directory-walker", choices=("os", "pathlib", "glob"))
    parser.add_argument("-r", "--reader", choices=("re", "etree", "feedparser"))
    parser.add_argument("-s", "--start", help="date à partir de laquelle on conserve les articles")
    parser.add_argument("-c", "--categories", nargs="*")
    args = parser.parse_args()

    if args.categories is None:
        args.categories = []

    walker = name_to_walker.get(args.directory_walker)
    if walker is None:
        raise ValueError(f"Invalid value for directory walker: {args.directory_walker}")

    reader = name_to_reader.get(args.reader)
    if reader is None:
        raise ValueError(f"Invalid value for RSS reader: {args.reader}")

    files = walker(args.rss_feed)

    articles = []
    for feed in files:
        articles.extend(reader(feed))

    # filtrage
    filtres = build_filters(args)
    articles = filtrage(filtres, articles)

    for article in articles:
        for key in ("id", "source", "title", "description", "date", "categories"):
            print(key, ":", article[key])
        print()


name_to_reader = {
    "re": rss_reader_re,
    "etree": rss_reader_etree,
    "feedparser": rss_reader_feedparser
}

name_to_walker = {
    "os": walk_os,
    "pathlib": walk_pathlib,
    "glob": walk_glob
}


if __name__ == "__main__":
    main()
