

import feedparser
import argparse

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
        source = (chemin.split('/') [-1]).replace('%20', " ")
        # Corr: modifier 'category'
        category = global_categories | set(t["term"] for t in entry.get("tags", []))

        metadonnées = {
            "id":ID,
            "source": source,
            "title":titre,
            "description":description,
            "date":date, 
            # Corr: modifier 'category'
            "category": sorted(category)
        }

        metadata.append(metadonnées)

        return(metadata)

def main():
    # Définition des arguments nécessaires en bash
    parser = argparse.ArgumentParser()
    parser.add_argument("output_file") # On devra donner le nom du fichier de sortie en argument quand on appellera le script en bash

    args = parser.parse_args()

    # Définition du chemin d'accès en évitant une erreur potentielle grâce à "try/except"
    try:
        chemin = input("Entrez le chemin d'accès au fichier :")
    except:
        print("Ce fichier n'existe pas.")

    metadata = rss_reader_r3(chemin)

    # Définition et remplissage du fichier de sortie
    with open(args.output_file, 'w') as file:
        for entry in metadata:
            file.write(f"id : {entry['id']}\n")
            file.write(f"source : {entry['source']}\n")
            file.write(f"title : {entry['title']}\n")
            file.write(f"description : {entry['description']}\n")
            file.write(f"date : {entry['date']}\n")
            file.write(f"category : {entry['category']}\n")
            file.write("\n")


if __name__ == "__main__":
    main()
