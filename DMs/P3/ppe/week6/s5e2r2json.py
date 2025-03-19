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
    raise NotImplementedError("Cette fonction n'a pas encore été implémentée.")

def load_xml(input_file: Path) -> Corpus:
    raise NotImplementedError("Cette fonction n'a pas encore été implémentée.")

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
    raise NotImplementedError("Cette fonction n'a pas encore été implémentée.")

def load_pickle(input_file: Path) -> Corpus:
    raise NotImplementedError("Cette fonction n'a pas encore été implémentée.")


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