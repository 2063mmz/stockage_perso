import argparse
import datetime
import feedparser
import glob
import html
import os
import re
import sys
from pathlib import Path

def sanitize_text(text):
    """ Nettoyage du texte : suppression des balises CDATA, HTML et des espaces inutiles """
    if text.startswith("<![CDATA[") and text.endswith("]]>"):
        text = text[9:-3]  # Supprimer les balises CDATA
    text = re.sub(r'<.*?>', '', text)  # Supprimer les balises HTML
    text = html.unescape(text)  # Convertir les entités HTML (&amp;, &lt;, etc.)
    return text.strip()  # Supprimer les espaces en début et fin de chaîne

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

def rss_reader_r1(chemin : str) -> list:
    """
    r1
    Cette fonction permet de lire un fichier RSS
    et d'en extraire les informations
    """
    metadata = [] # Liste qui contiendra les informations extraites du fichier RSS

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
            'title': sanitize_text(title_match.group(1)) if title_match else "",
            'description': sanitize_text(desc_match.group(1)) if desc_match else "",
            'date': date_match.group(1) if date_match else "",
            'categories': category_list if category_list else ""
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
    for entry in fichier.entries:
        ID = entry.link
        titre = entry.title
        description = entry.description
        date = entry.published
        source = (chemin.split('/')[-1]).replace('%20', " ")
        categories = getattr(entry, 'tags', [])
        category_list = [category.term for category in categories] if categories else ['No category']

        metadata.append({
            "id": ID,
            "source": source,
            "title": titre,
            "description": description,
            "date": date,
            "categories": category_list
        })

    return(metadata)

def filtre_r1(item: dict, date_debut=None, date_fin=None) -> bool:
    """
    Filtre les articles en fonction de leur date de publication.

    Args:
        item (dict): Un dictionnaire représentant un article RSS avec une clé 'date'
        date_debut (datetime.datetime, optional): Date à partir de laquelle on conserve les articles
        date_fin (datetime.datetime, optional): Date jusqu'à laquelle on conserve les articles

    Returns:
        bool: True si l'article doit être conservé, False sinon
    """
    if 'date' not in item or not item['date']:
        return False
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z',  # RFC 822/1123 format
        '%a, %d %b %Y %H:%M:%S %Z',  # Variation with timezone name
        '%a, %d %b %Y %H:%M:%S',      # Without timezone
        '%Y-%m-%dT%H:%M:%S%z',       # ISO 8601 format
        '%Y-%m-%dT%H:%M:%SZ',        # ISO 8601 UTC
        '%Y-%m-%d %H:%M:%S',         # Basic datetime format
        '%d %b %Y %H:%M:%S',         # Another common format
        '%a %b %d %H:%M:%S %Y',      # Yet another format
    ]
    try:
        for form in date_formats:
            try:
                date_article = datetime.datetime.strptime(item['date'], form)
                break
            except ValueError:
                continue
        if not date_article:
            return False
        if date_debut and date_article < date_debut:
            return False
        if date_fin and date_article > date_fin:
            return False
        return True
    except Exception:
        return False

def filtrage(filtres: list, articles: list) -> list:
    resultat = []
    for article in articles:
        keep = True
        for filtre in filtres:
            if not filtre(article):
                keep = False
                break
        if keep:
            resultat.append(article)
    return resultat

def main():
    """
    Fonction principale qui gère:
    1. Le parsing des arguments de ligne de commande
    2. La récupération du chemin du corpus
    3. L'analyse des fichiers XML selon la méthode choisie
    4. L'enregistrement des résultats dans des fichiers texte
    """
    parser = argparse.ArgumentParser(prog='rss_reader')
    parser.add_argument('method', choices=["re", "etree", "feedparser"],
                        help="Méthode d'analyse des fichiers XML")
    parser.add_argument('--date_debut', type=str,
                        help="Date de début pour le filtrage (YYYY-MM-DD)")
    parser.add_argument('--date_fin', type=str,
                       help="Date de fin pour le filtrage (YYYY-MM-DD)")
    args = parser.parse_args()
    choix = args.method

    # Filtre: date args
    date_format = '%Y-%m-%d'
    date_debut = datetime.datetime.strptime(args.date_debut, date_format) if args.date_debut else None
    date_fin = datetime.datetime.strptime(args.date_fin, date_format) if args.date_fin else None

    chemin = input("Veuillez entrer le chemin du dossier corpus: ").strip()
    # Vérifier si le fichier existe
    if not os.path.exists(chemin):
        print(f"Erreur : Le dossier '{chemin}' n'existe pas.")
        return

    reader_funcs = {
        "re": [get_files_r1 ,rss_reader_r1],
        "etree": [get_files_r2 ,rss_reader_r2],
        "feedparser": [get_files_r3 ,rss_reader_r3]
    }
    files = reader_funcs[choix][0](chemin)
    if not files:
        print(f"Aucun fichier XML trouvé dans le répertoire: {chemin}")
        return

    for file in files:
        res = reader_funcs[choix][1](file)
        if not res:
            print(f"Pour le ficher {file}, aucune information n'a été trouvée.")
        # Run Filter: date
        if date_debut or date_fin:
            res = filtrage([lambda item : filtre_r1(item, date_debut, date_fin)], res)
            #print(f"File: {file}, {len(res)} articles après filtrage par date")
        if not res:
            continue

    # Créer un fichier de sortie
        output_file = file.split('/')[-1].replace('.xml', '.txt')

        with open(output_file, 'w', encoding='utf-8') as f:
            for item in res:
                f.write(f"id : {item['id']}\n")
                f.write(f"source : {item['source']}\n")
                f.write(f"title : {item['title']}\n")
                f.write(f"description : {item['description']}\n")
                f.write(f"date : {item['date']}\n")
                f.write(f"categories : {item['categories']}\n")
                f.write('\n')  # Ligne vide entre chaque item

    print(f"Les informations ont été enregistrées")

if __name__ == '__main__':
    main()

