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
from dataclasses import dataclass, field

@dataclass
class Article:
    id: str
    source: str
    title: str
    description: str
    date: str
    categories: list[str] = field(default_factory=list)

def nettoyage(texte):
    texte_net = re.sub(r"<!\[CDATA\[(.*?)\]\]>", "\\1", texte, flags=re.DOTALL)
    texte_net = html.unescape(texte_net)
    texte_net = re.sub("<.+?>", "", texte_net)
    texte_net = re.sub("\n+", " ", texte_net)
    texte_net = texte_net.strip()
    return texte_net

def rss_reader_re(filename: str | Path) -> list[Article]:
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

            article = Article(
                id=dataid,
                source=name,
                title=title,
                description=description,
                date=pubdate,
                categories=sorted(local_categories),
            )
            articles.append(article)

    return articles

def rss_reader_etree(filename: str | Path) -> list[Article]:
    name = Path(filename).name

    if name.lower() in ("flux.xml", "flux rss.xml"):  # erreur de parsing
        return []

    try:
        root = ET.parse(filename)
    except ET.ParseError:
        return []

    articles = []
    global_categories = set(element.text.strip() for element in root.iterfind("./channel/category"))

    for item in root.iterfind(".//item"):
        dataid = item.find("guid").text

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

        article = Article(
            id=dataid,
            source=name,
            title=title,
            description=description,
            date=pubdate or "",
            categories=sorted(local_categories),
        )
        articles.append(article)

    return articles

def rss_reader_feedparser(filename: str | Path) -> list[Article]:
    name = Path(filename).name
    feed = feedparser.parse(filename)
    articles = []
    global_categories = set([item["term"] for item in feed["feed"].get("tags", [])])

    for item in feed["entries"]:
        pubdate = item.get("published")
        if not pubdate:
            pubdate = item.get("lastpublicationdate")

        categories = global_categories | set(t["term"] for t in item.get("tags", []))

        article = Article(
            id=item.id,
            source=name,
            title=nettoyage(item.title),
            description=nettoyage(item.get("description")),
            date=pubdate or "",
            categories=sorted(categories),
        )
        articles.append(article)

    return articles

def main():
    parser = argparse.ArgumentParser(description="foobar")
    parser.add_argument("rss_feed")
    parser.add_argument("-r", "--reader", choices=("re", "etree", "feedparser"))
    args = parser.parse_args()

    reader = name_to_reader.get(args.reader)
    if reader is None:
        raise ValueError(f"Invalid value for RSS reader: {args.reader}")

    articles = reader(args.rss_feed)

    for article in articles:
        for key in ("id", "source", "title", "description", "date", "categories"):
            print(key, ":", getattr(article, key))
        print()

name_to_reader = {
    "re": rss_reader_re,
    "etree": rss_reader_etree,
    "feedparser": rss_reader_feedparser
}

if __name__ == "__main__":
    main()
