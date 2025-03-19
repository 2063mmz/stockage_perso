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

def replace_html_entities(xml_content: str) -> str:
    """
    Remplace les entités HTML dans le contenu XML par leurs équivalents XML.
    """
    # Remplace les entités HTML par leurs caractères correspondants en XML
    return html.unescape(xml_content)   

def sanitize_xml_content(xml_content: str) -> str:
    """
    Remplace les entités malformées ou non échappées comme '&'.
    """
    # Remplacer & par &amp; dans les titres et descriptions
    xml_content = xml_content.replace("&", "&amp;")
    return xml_content 

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



def rss_reader_r2(corpus_dir: str, keywords: List[str]) -> List[Dict]:
    """
    Lire tous les fichiers XML dans un dossier dont le nom contient au moins un des mots-clés.
    Retourne une liste de dictionnaires représentant les articles.
    """
    all_articles = []
    corpus_path = Path(corpus_dir)

    if not corpus_path.exists() or not corpus_path.is_dir():
        print(f"Dossier invalide : {corpus_dir}")
        return all_articles

    # Sélectionner les fichiers XML contenant au moins un mot-clé
    xml_files = [
        f for f in glob.glob(str(corpus_path / "**/*.xml"), recursive=True)
        if any(keyword.lower() in Path(f).name.lower() for keyword in keywords)
    ]

    if not xml_files:
        print(f"Aucun fichier XML contenant {keywords} trouvé.")
        return all_articles

    for xml_file in xml_files:
        try:
            print(f"Tentative de lecture du fichier : {xml_file}")
            
            with open(xml_file, 'r', encoding='utf-8') as f:
                xml_content = f.read()
            
            # Remplacer les entités HTML par les caractères XML correspondants
            xml_content = replace_html_entities(xml_content)

            # Remplacer les entités malformées avant le parsing
            xml_content = sanitize_xml_content(xml_content)

            # Parser le contenu corrigé
            tree = ET.ElementTree(ET.fromstring(xml_content))
            root = tree.getroot()

            for item in root.findall(".//item"):
                article = {
                    "id": item.find("link").text if item.find("link") is not None else "",
                    "titre": item.find("title").text if item.find("title") is not None else "",
                    "description": item.find("description").text if item.find("description") is not None else "",
                    "date": item.find("pubDate").text if item.find("pubDate") is not None else "",
                    "categories": [cat.text for cat in item.findall("category") if cat.text],
                    "source": Path(xml_file).name
                }
                all_articles.append(article)

        except ET.ParseError as e:
            # Affichage d'une erreur spécifique pour les fichiers XML malformés
            print(f"Erreur de parsing XML dans le fichier {xml_file}: {e}")
        except Exception as e:
            # Gestion des autres erreurs
            print(f"Erreur inattendue lors de la lecture du fichier {xml_file}: {e}")

    return all_articles


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
        category_list = global_categories | set(t["term"] for t in entry.get("tags", []) if "term" in t)

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
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%d %b %Y %H:%M:%S',
        '%a %b %d %H:%M:%S %Y',

    ]
    date_article = None
    for form in date_formats:
        try:
            date_article = datetime.datetime.strptime(item['date'], form)
            break
        except ValueError:
            continue

    if date_article is None:
        return False

    date_article = date_article.replace(tzinfo=None)
    return True

    

def filtre_r2(articles: List[Dict]) -> List[Dict]:
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



def filtre_r3(categorie_choisie: str) -> Callable[[dict], bool]:
    def filtre(item: dict) -> bool:
        categories = item.get('categories', [])
        # Comparaison insensible à la casse
        return any(categorie_choisie.lower() == cat.lower() for cat in categories)
    return filtre

def filtrage(filtres: list, articles: list) -> list:
    """
    Applique une liste de filtres aux articles.
    """

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
    parser.add_argument('-m', '--method', choices=["re", "etree", "feedparser"],
                        help="Méthode d'analyse des fichiers XML")
    parser.add_argument('-dd','--date_debut', type=str, default=None,
                        help="Date de début pour le filtrage (YYYY-MM-DD)")
    parser.add_argument('-df', '--date_fin', type=str, default=None,
                        help="Date de fin pour le filtrage (YYYY-MM-DD)")
    parser.add_argument('-s', '--source', type=str, default="",
                        help="Source d'article à filtrer")
    parser.add_argument('-c', '--categorie', type=str, default="",
                        help="Catégorie d'article à filtrer")
    
    # Si aucun paramètre n'est saisi, afficher le message d'aide et quitter la fonction
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    choix = args.method
    
    # Filtre: date args
    date_format = '%Y-%m-%d' 
    date_debut = datetime.datetime.strptime(args.date_debut, date_format) if args.date_debut else None
    date_fin = datetime.datetime.strptime(args.date_fin, date_format) if args.date_fin else None
    '''
    if not (date_debut or date_fin):
        user_date_debut = input("Entrez la date de début (YYYY-MM-DD) ou laissez vide: ").strip()
        user_date_fin = input("Entrez la date de fin (YYYY-MM-DD) ou laissez vide: ").strip()
    if user_date_debut:
        date_debut = datetime.datetime.strptime(user_date_debut, date_format)
    if user_date_fin:
        date_fin = datetime.datetime.strptime(user_date_fin, date_format)
    '''

    chemin = input("Veuillez entrer le chemin du dossier corpus: ").strip()
    # Vérifier si le fichier existe
    if not Path(chemin).exists():
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
        # Run Filter: source
        # Filtre: source
        if choix == "etree":
            keywords = [args.source] if args.source else []
            res = rss_reader_r2(file, keywords)
        else:
            res = reader_funcs[choix][1](file)  

        # Run Filter: date
        filtres = []
        if date_debut or date_fin:
            filtres.append(lambda item: filtre_r1(item, date_debut, date_fin))
        res = filtrage(filtres, res)

        # Run Filter: source
        # Filtre: source
        if args.source and choix != "etree":
            res = [item for item in res if args.source.lower() in item["source"].lower()]

        # Run Filter: categories
        # Filtre: categories
        if args.categorie:
            filter_func = filtre_r3(args.categorie)
            res = [item for item in res if filter_func(item)]

        if not res:
            print(f"Pour le fichier {file}, aucune information n'a été trouvée.")
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