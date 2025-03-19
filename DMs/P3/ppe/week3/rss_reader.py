import os
import sys
import re

def nettoyer_texte(texte):

    texte = re.sub(r"<!\[CDATA\[(.*?)\]\]>", r"\1", texte)
    texte = re.sub(r"<[^>]+>", "", texte)

    return texte.strip()

def extraire_articles_rss(fichier_rss):

    with open(fichier_rss, "r", encoding="utf-8") as f:
        xml_content = f.read()

    source = os.path.basename(fichier_rss)
    articles = []
    items = re.findall(r"<item>(.*?)</item>", xml_content, re.DOTALL)

    for item in items:
        article = {
            "id": re.search(r"<guid>(.*?)</guid>", item).group(1) if re.search(r"<guid>(.*?)</guid>", item) else "Sans ID",
            "source": source,
            "title": nettoyer_texte(re.search(r"<title>(.*?)</title>", item).group(1)) if re.search(r"<title>(.*?)</title>", item) else "Sans titre",
            "description": nettoyer_texte(re.search(r"<description>(.*?)</description>", item).group(1)) if re.search(r"<description>(.*?)</description>", item) else "Sans contenu",
            "date": re.search(r"<pubDate>(.*?)</pubDate>", item).group(1) if re.search(r"<pubDate>(.*?)</pubDate>", item) else "Sans date",
            "categories": re.findall(r"<category>(.*?)</category>", item)
        }
        articles.append(article)

    return articles

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python rss_reader.py fichier.xml")
        sys.exit(1)

    fichier_rss = sys.argv[1]
    articles = extraire_articles_rss(fichier_rss)

    if articles:
        for article in articles:
            print(f"id : {article['id']}")
            print(f"source : {article['source']}")
            print(f"title : {article['title']}")
            print(f"description : {article['description']}")
            print(f"date : {article['date']}")
            print(f"categories : {article['categories']}\n")
