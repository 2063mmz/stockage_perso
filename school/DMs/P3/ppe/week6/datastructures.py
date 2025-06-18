import json
import pickle
import xml.etree.ElementTree as ET
from argparse import ArgumentParser
from dataclasses import dataclass,asdict
from typing import Any, List
from pathlib import Path

@dataclass
class Article:
    id: str
    source: str
    title: str
    description: str
    date: str
    categories: List[str]

@dataclass
class Corpus:
    articles: List[Article]

    def to_dict(self) -> dict:
        return {"articles": [asdict(article) for article in self.articles]}

    @classmethod
    def from_dict(cls, data: dict) -> "Corpus":
        articles = [Article(**article) for article in data["articles"]]
        return cls(articles)
 
"""
r1
"""
def save_xml(corpus: Corpus, output_file: Path) -> None:
    root = ET.Element("corpus")
    for article in corpus.articles:
        article_elem = ET.SubElement(root, "article")
        for key, value in asdict(article).items():
            field_elem = ET.SubElement(article_elem, key)
            field_elem.text = str(value)
    tree = ET.ElementTree(root)
    tree.write(output_file, encoding='utf-8', xml_declaration=True)

def load_xml(input_file: Path) -> Corpus:
    articles = []
    RELEVANT_ELEMENTS = ["title", "link", "description", "content", "author", "date"]
    tree = ET.parse(input_file)
    root = tree.getroot()
    feed_categories = [cat.text.strip() for cat in root.findall("./channel/category")]
    for item in root.findall(".//item"):
        entry = {"source": input_file.name}
        guid = item.find("guid")
        if guid is not None and guid.text:
            entry["id"] = guid.text
        else:
            link = item.find("link")
            if link is not None and link.text:
                entry["id"] = link.text
            else:
                entry["id"] = "No ID"

        for elt in RELEVANT_ELEMENTS:
            node = item.find(elt)
            if node is not None and node.text:
                entry[elt] = (node.text)  # Utilisation de sanitize_text

        pub_date = item.find("pubDate")
        if pub_date is not None:
            entry["date"] = pub_date.text

        item_categories = [cat.text.strip() for cat in item.findall("category")]
        categories = feed_categories.copy()
        categories.extend(item_categories)
        entry["categories"] = sorted(set(categories))

        article = Article(
            id=entry.get('id', ''),
            source=entry.get('source', ''),
            title=entry.get('title', ''),
            description=entry.get('description', ''),
            date=entry.get('date', ''),
            categories=entry.get('categories', [])
        )

        articles.append(article)

    return Corpus(articles)

"""
r2
"""
def save_json(corpus: Corpus, output_file: Path) -> None:
        data = corpus.to_dict()
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Corpus sauvegardé dans {output_file}")

def load_json(input_file: Path) -> Corpus:
     with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
            return Corpus.from_dict(data)

"""
r3
"""
def save_pickle(corpus: Corpus, output_file: Path) -> None:
    # Écrire les fichier xml en format binaire dans out_put pour le sauvegarder
    with open(output_file, "wb") as f:  
        pickle.dump(corpus, f)

def load_pickle(input_file: Path) -> Corpus:
     # Désérialiser les données et les reconstruit sous forme de liste
    with open(input_file, "rb") as f:
        return pickle.load(f)

def main():
    parser = ArgumentParser(description="Convertir les fichiers de format XML, JSON, et Pickle.")
    parser.add_argument("input_file", type=Path, help="Input file path")
    parser.add_argument("output_file", type=Path, help="Output file path")
    parser.add_argument("--from-format", choices=["xml", "json", "pickle"], required=True, help="Input file format")
    parser.add_argument("--to-format", choices=["xml", "json", "pickle"], required=True, help="Output file format")
    args = parser.parse_args()

    # Vérifier si le fichier d'entrée existe
    if not args.input_file.exists():
        print(f"Erreur : le fichier d'entrée '{args.input_file}' n'existe pas.")
        return
    try:
        load_func = globals()[f"load_{args.from_format}"]
        save_func = globals()[f"save_{args.to_format}"]
        corpus = load_func(args.input_file)
        # Sauvegarde du fichier
        save_func(corpus, args.output_file)
        print(f"Enregistrement des données dans le fichier {args.output_file} avec la fonction {save_func.__name__}")
    except KeyError as e:
        print(f"Erreur : format '{e.args[0]}' non pris en charge pour la fonction de conversion.")

if __name__ == "__main__":
     main()
