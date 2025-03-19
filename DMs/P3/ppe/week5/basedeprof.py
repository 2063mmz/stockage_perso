from typing import Callable, List, Dict, Set
import argparse
import re
import sys
import html
import os.path
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET
import feedparser
from datastructures import Article, Corpus

'''
Le format de la commande: python rss_parcours.py corpus -w pathlib -r feedparser -s 01/01/24 -c Football
'''

def nettoyage(texte: str) -> str:

    texte_net = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", texte, flags=re.DOTALL)
    texte_net = html.unescape(texte_net)
    texte_net = re.sub(r"<.+?>", "", texte_net, flags=re.DOTALL | re.IGNORECASE)
    texte_net = re.sub(r"\n+", " ", texte_net)
    return texte_net.strip()


def rss_reader_re(filename: str | Path) -> list[Dict]:
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


def rss_reader_etree(filename: str | Path) -> list[Dict]:
    name = Path(filename).name

    if name.lower() in ("flux.xml", "flux rss.xml"):  # fichiers connus pour poser problème
        return []

    try:
        tree = ET.parse(filename)
    except ET.ParseError as e:
        print(f"Erreur de parsing dans {filename}: {e}")
        return []

    root = tree.getroot()
    articles = []
    global_categories = set()
    for element in root.iterfind("./channel/category"):
        if element.text:
            global_categories.add(element.text.strip())

    for item in root.iterfind(".//item"):
        dataid = item.find("guid").text if item.find("guid") is not None else ""

        title_element = item.find("title")
        title = nettoyage(title_element.text) if (title_element is not None and title_element.text) else ""

        description_element = item.find("description")
        description = nettoyage(description_element.text) if (description_element is not None and description_element.text) else ""

        pubdate_element = item.find("pubDate")
        if pubdate_element is None:
            pubdate_element = item.find("lastpublished")
        pubdate = nettoyage(pubdate_element.text) if (pubdate_element is not None and pubdate_element.text) else ""

        local_categories = global_categories.copy()
        for category_element in item.iterfind("category"):
            if category_element.text:
                local_categories.add(category_element.text.strip())

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


def rss_reader_feedparser(filename: str | Path) -> list[Dict]:
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
    result = []
    for dirpath, _, filenames in os.walk(path):
        for file in filenames:
            if file.lower().endswith(".xml"):
                result.append(os.path.join(dirpath, file))
    return sorted(result)


def walk_pathlib(path: str) -> list[str]:
    filepath = Path(path)
    if filepath.is_file():
        return [str(filepath)] if filepath.suffix.lower() == ".xml" else []
    result = []
    for file in sorted(filepath.iterdir()):
        if file.is_file() and file.suffix.lower() == ".xml":
            result.append(str(file))
        elif file.is_dir():
            result.extend(walk_pathlib(str(file)))
    return result


def walk_glob(path: str) -> list[str]:
    return sorted(str(f) for f in Path(path).glob("**/*.xml"))


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


def create_filter_source(articles: List[Dict]) -> List[Dict]:
    """
    Supprimer les articles en double en utilisant 'titre + description' comme clé.
    """
    seen: Set[str] = set()
    unique_articles = []

    for article in articles:
        unique_key = f"{article['titre']}|{article['description']}"

        if unique_key not in seen:
            seen.add(unique_key)
            unique_articles.append(article)

    return unique_articles


def create_filter_categories(categories: list[str]) -> Callable[[Dict], bool]:
    cat_set = set(categories)
    def filtre(a: dict) -> bool:
        return len(cat_set.intersection(a['categories'])) > 0
    return filtre


def build_filters(args: argparse.Namespace) -> list[Callable[[Dict], bool]]:
    filtres = []
    if args.start:
        filtres.append(create_filter_start_date(args.start))
    if args.categories:
        filtres.append(create_filter_categories(args.categories))
    return filtres


def filtrage(filtres: list[Callable[[Dict], bool]], articles: list[Dict]) -> list[Dict]:
    resultat = []
    for a in articles:
        if all([f(a) for f in filtres]):
            resultat.append(a)
    return resultat

def main():
    parser = argparse.ArgumentParser(description="RSS Reader")

    parser.add_argument("rss_feed", help="Fichier ou dossier contenant le flux RSS")
    parser.add_argument("-w", "--directory-walker", choices=("os", "pathlib", "glob"), required=True,
                        help="Méthode de recherche des fichiers")
    parser.add_argument("-r", "--reader", choices=("re", "etree", "feedparser"), required=True,
                        help="Méthode d'analyse du RSS")
    parser.add_argument("-s", "--start", help="Date à partir de laquelle conserver les articles (format: dd/mm/yy)")
    parser.add_argument("-o", "--source", nargs="*", default=[],
                        help="Source pour filtrer les articles")
    parser.add_argument("-c", "--categories", nargs="*", default=[],
                        help="Catégories pour filtrer les articles")
    args = parser.parse_args()
    
    if args.categories is None:
        args.categories = []

    if args.source is None:
        args.source = []

    walker = name_to_walker.get(args.directory_walker)
    if walker is None:
        raise ValueError(f"Invalid directory walker: {args.directory_walker}")

    reader = name_to_reader.get(args.reader)
    if reader is None:
        raise ValueError(f"Invalid RSS reader: {args.reader}")

    files = walker(args.rss_feed)
    if not files:
        print("Aucun fichier xml trouvé.")
        sys.exit(1)
        
    articles = []
    for file in files:
        articles.extend(reader(file))

    # filtrage
    filtres = build_filters(args)
    articles = filtrage(filtres, articles)

    articles_objs = [Article(**article) for article in articles]
    corpus = Corpus(articles=articles_objs)

    for article in corpus.articles:
        print(f"Id: {article.id}")
        print(f"Source: {article.source}")
        print(f"Title: {article.title}")
        print(f"Description: {article.description}")
        print(f"Date: {article.date}")
        print(f"Categories: {article.categories}")
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
