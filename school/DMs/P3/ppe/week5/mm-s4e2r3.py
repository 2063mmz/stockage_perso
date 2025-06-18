#!/usr/bin/env python3
import re
import xml.etree.ElementTree as ET
import os
import feedparser
import argparse
import sys
# Corr: importer des modules
from pathlib import Path
from typing import Callable, List, Dict, Set

def rss_reader_r1(chemin: str) -> list:
    metadata = []
    try:
        with open(chemin, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return []

    items = re.findall(r'<item>(.*?)</item>', content, re.DOTALL)
    for item in items:
        id_match = re.search(r'<link>(.*?)</link>', item)
        title_match = re.search(r'<title>(.*?)</title>', item)
        desc_match = re.search(r'<description>(.*?)</description>', item)
        date_match = re.search(r'<pubDate>(.*?)</pubDate>', item)
        categories = re.finditer(r'<category[^>]*>(.*?)</category>', item)
        category_list = [cat.group(1) for cat in categories]

        item_dict = {
            'id': id_match.group(1) if id_match else "",
            'source': f"{chemin.split('/')[-1]}",
            'title': title_match.group(1) if title_match else "",
            'description': desc_match.group(1) if desc_match else "",
            'date': date_match.group(1) if date_match else "",
            'categories': category_list
        }
        metadata.append(item_dict)
    return metadata

def rss_reader_r2(chemin: str) -> list:
    metadata = []
    try:
        tree = ET.parse(chemin)
        root = tree.getroot()
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier: {e}")
        return []

    for item in root.findall(".//item"):
        id_ = item.find("link").text if item.find("link") is not None else ""
        title = item.find("title").text if item.find("title") is not None else ""
        description = item.find("description").text if item.find("description") is not None else ""
        date = item.find("pubDate").text if item.find("pubDate") is not None else ""
        categories = [cat.text for cat in item.findall("category") if cat.text]

        metadata.append({
            "id": id_,
            "source": os.path.basename(chemin),
            "title": title,
            "description": description,
            "date": date,
            "categories": categories
        })
    return metadata

def rss_reader_r3(chemin: str) -> list:
    fichier = feedparser.parse(chemin)
    metadata = []
    # Corr: ajouter d'un code 
    global_categories = set([item["term"] for item in fichier["feed"].get("tags", [])])

    for entry in fichier.entries:
        ID = entry.link
        titre = entry.title
        description = entry.description
        date = entry.published
        source = (chemin.split('/')[-1]).replace('%20', " ")
        # Corr: modifier 'category'
        category_list = global_categories | set(t["term"] for t in entry.get("tags", []))

        metadata.append({
            "id": ID,
            "source": source,
            "title": titre,
            "description": description,
            "date": date,
            # Corr: modifier 'category'
            "categories": sorted(category_list)
        })

    return(metadata)

def create_filter_categorie(categorie_choisie: str) -> Callable[[dict], bool]:
    def filtre(item: dict) -> bool:
        categories = item.get('categories', [])
        # Comparaison insensible à la casse
        return any(categorie_choisie.lower() == cat.lower() for cat in categories)
    return filtre

def main():
    parser = argparse.ArgumentParser(description="RSS Reader")

    # Définition des arguments en bash
    parser.add_argument("method", choices=["re", "etree", "feedparser"], help="Choose the method for parsing the RSS feed")
    parser.add_argument("directory", help="Directory containing RSS files")
    args = parser.parse_args()

    try:
        files = os.listdir(args.directory)
    except FileNotFoundError:
        print("The directory does not exist.")
        return

    method = args.method

    # Choix de la méthode
    if method == "re":
        reader_func = rss_reader_r1
    elif method == "etree":
        reader_func = rss_reader_r2
    elif method == "feedparser":
        reader_func = rss_reader_r3
    # Corr: ajouter '.strip()' pour supprimer les espaces des deux côtés d'un input
    categorie_choisie = input("Entrez une catégorie d'article :").strip()
    
    # Générer le filtre à partir de la catégorie saisie
    filter_func = create_filter_categorie(categorie_choisie)

    # Traitement des fichiers
    rss_files = [f for f in files if os.path.isfile(os.path.join(args.directory, f))]
    for filename in rss_files:
        filepath = os.path.join(args.directory, filename)
        print(f"Traitement du fichier {filepath}")

        metadata = reader_func(filepath)
        if not metadata:
            print(f"Rien dans {filepath}")
            continue

        metadonnees_filtrees = [item for item in metadata if filter_func(item)]

        # Création du fichier de sortie
        output_file = filename.split('/')[-1].replace('.xml', '.txt')

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for item in metadata:
                    f.write(f"id : {item['id']}\n")
                    f.write(f"source : {item['source']}\n")
                    f.write(f"title : {item['title']}\n")
                    f.write(f"description : {item['description']}\n")
                    f.write(f"date : {item['date']}\n")
                    f.write(f"categories : {item['categories']}\n")
                    f.write('\n')

            print(f"Les données ont été ajoutées à {output_file}")
        except:
            print(f"Erreur dans le remplissage de {output_file}")

        try:
            with open(f"{categorie_choisie}.txt", "a", encoding="utf-8") as f:
                for item in metadonnees_filtrees:
                    f.write(f"id : {item['id']}\n")
                    f.write(f"source : {item['source']}\n")
                    f.write(f"title : {item['title']}\n")
                    f.write(f"description : {item['description']}\n")
                    f.write(f"date : {item['date']}\n")
                    f.write(f"categories : {item['categories']}\n")
                    f.write('\n')
            print(f"Les données filtrées ont été ajoutées au fichier {categorie_choisie}.txt")
        except Exception as e:
            print(f"Erreur dans le remplissage de {categorie_choisie}.txt: {e}")

if __name__ == '__main__':
    main()
