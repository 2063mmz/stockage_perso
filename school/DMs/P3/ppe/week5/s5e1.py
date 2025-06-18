import argparse
import datetime
import feedparser
import glob
import html
import os
import re
import sys
from pathlib import Path
from typing import Callable, List, Dict, Set
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field


@dataclass
class chemin:
    chemin : str
    item: dict
    categorie_choisie: str
    filtres: list
    articles: list
corpus = elements("")


## lire dossier##########################################

def get_files_r1(chemin : str) -> list:
    """
    Récupère récursivement tous les fichiers .xml en utilisant
    la bibliothèque pathlib mais sans utiliser glob.
    """
    p = Path(chemin)
    files = []
    for x in p.iterdir():
        if x.is_file() and x.suffix == '.xml':
            files.append(str(x.resolve()))
        elif x.is_dir():
            files.extend(get_files_r1(x))
    return files

def get_files_r2(corpus_dir: str) -> list:
    """
    Récupère tous les fichiers XML dans le dossier avec glob.
    """
    # Convertir le chemin en objet Path
    corpus_path = Path(corpus_dir)

    # Vérifier si le chemin existe
    if not corpus_path.exists() or not corpus_path.is_dir():
        print(f"Le chemin spécifié n'est pas un dossier valide : {corpus_dir}")
        return []

    # Utiliser glob pour rechercher tous les fichiers XML dans l'arborescence (avec **)
    return glob.glob(str(corpus_path) + "/**/*.xml", recursive=True)

def get_files_r3(corpus_dir: str) -> list:
    filepath = []
    try:
        files = os.listdir(corpus_dir)
    except FileNotFoundError:
        print(f"Le chemin spécifié n'est pas un dossier valide : {corpus_dir}")
        return []
    
    for filename in files:
        full_path = os.path.join(corpus_dir, filename)
        if os.path.isfile(full_path) and filename.lower().endswith('.xml'):
            filepath.append(full_path)
        elif os.path.isdir(full_path):
            filepath.extend(get_files_r3(full_path))

    return filepath

def main ():

    parser = argparse.ArgumentParser(prog='rss_reader')
    parser.add_argument('-m','--method', choices=["re", "etree", "feedparser"],
                        help="Méthode d'analyse des fichiers XML")
    parser.add_argument('-p','--path', choices=[" pathlib", "glob", "os"],
                        help="Méthode de récupère le dossier")
    parser.add_argument('-dd','--date_debut', type=str, default=None,
                        help="Date de début pour le filtrage (YYYY-MM-DD)")
    parser.add_argument('-df','--date_fin', type=str, default=None,
                       help="Date de fin pour le filtrage (YYYY-MM-DD)")
    parser.add_argument('-c', '--categorie', type=str, default="",
                    help="Catégorie d'article à filtrer")
    
    # Si aucun paramètre n'est saisi, afficher le message d'aide et quitter la fonction
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    choix = args.method
    choix_path = args.path

    
