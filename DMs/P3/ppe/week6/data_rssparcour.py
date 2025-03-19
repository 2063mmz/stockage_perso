from typing import Callable
import argparse
import sys
import os.path
from typing import List, Dict, Set
from datetime import datetime
from pathlib import Path
from xml.etree import ElementTree as ET


'''
Le format de la commande: python rss_parcours.py corpus -w pathlib -r feedparser -s 01/01/24 -c Football
'''
from rss_reader import name_to_reader

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


def create_filter_categories(categories: list[str]) -> Callable[[dict], bool]:
    cat_set = set(categories)
    def filtre(a: dict) -> bool:
        return len(cat_set.intersection(a['categories'])) > 0
    return filtre


def build_filters(args: argparse.Namespace) -> list[Callable[[dict], bool]]:
    filtres = []
    if args.start:
        filtres.append(create_filter_start_date(args.start))
    if args.categories:
        filtres.append(create_filter_categories(args.categories))
    return filtres


def filtrage(filtres: list[Callable[[dict], bool]], articles: list[dict]) -> list[dict]:
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


    files = walker(args.rss_feed)
    if not files:
        print("Aucun fichier xml trouvé.")
        sys.exit(1)
        
    articles = []
    for file in files:
        articles.extend(name_to_reader(file))


    # filtrage
    filtres = build_filters(args)
    articles = filtrage(filtres, articles)

    for article in articles:
        for key in ("id", "source", "title", "description", "date", "categories"):
            print(f"{key} : {article[key]}")
        print()

name_to_walker = {
    "os": walk_os,
    "pathlib": walk_pathlib,
    "glob": walk_glob
}


if __name__ == "__main__":
    main()
