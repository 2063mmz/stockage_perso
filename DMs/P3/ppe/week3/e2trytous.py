import os
import re
import sys
import feedparser
from lxml import etree, html
from pathlib import Path

# R1
def read_rss_with_re(file_path):

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' n'existe pas.")
        return []
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier {file_path} : {e}")
        return []

    # Récupération de la catégorie principale du flux (si présente)
    channel_category_match = re.search(r"<channel>.*?<category>(.*?)</category>.*?</channel>",
                                       content, re.DOTALL)
    channel_category = channel_category_match.group(1).strip() if channel_category_match else ""

    # Expression régulière pour extraire les articles (<item>)
    pattern = re.compile(
        r"<item>.*?"
        r"<title><!\[CDATA\[(.*?)\]\]></title>.*?"
        r"<link>(.*?)</link>.*?"
        r"<pubDate>(.*?)</pubDate>.*?"
        r"<description><!\[CDATA\[(.*?)\]\]></description>.*?"
        r"</item>",
        re.DOTALL
    )

    items = []
    matches = pattern.findall(content)

    for match in matches:
        title_raw = match[0].strip()
        link_raw = match[1].strip()
        pubdate_raw = match[2].strip()
        description_raw = match[3].strip()

        # Nettoyage des balises HTML dans la description
        description_clean = re.sub(r"<.*?>", "", description_raw)

        item_dict = {
            "id": link_raw,
            "title": title_raw,
            "description": description_clean,
            "date": pubdate_raw,
            "categories": [channel_category] if channel_category else []
        }
        items.append(item_dict)

    return items

# La fonction ex2r1
def process_directory(directory_path):
    """
    Parcourt récursivement tous les fichiers XML du dossier donné et de ses sous-dossiers.
    """
    path = Path(directory_path)

    if not path.exists() or not path.is_dir():
        print(f"Erreur : Le dossier '{directory_path}' n'existe pas ou n'est pas valide.")
        sys.exit(1)

    all_items = []

    # Parcours récursif des fichiers XML sans utiliser glob()
    for file in path.rglob("*.xml"):
        print(f"Traitement de : {file}")
        items = read_rss_with_re(file)
        all_items.extend(items)

    if not all_items:
        print("Aucun article trouvé dans les fichiers du dossier.")
        return

    # Affichage des résultats
    for item in all_items:
        print(f"id : {item['id']}")
        print(f"title : {item['title']}")
        print(f"description : {item['description']}")
        print(f"date : {item['date']}")
        print(f"categories : {item['categories']}")
        print()

# R2
def read_rss_etree(file_path: str | Path )->list[dict[str, str]]:
    """
    Lit un fichier XML RSS et retourne les items avec leur texte et métadonnées.

    :param file_path: Chemin du fichier à traiter.
    :return: Liste de dictionnaires contenant les articles (id, source, titre, description, date, catégories).
    """

    name = Path(file_path).name

    if name.lower() in ("flux.xml", "flux rss.xml"):
        return []

    try:
        tree = etree.parse(file_path)
    except (etree.XMLSyntaxError, etree.ParseError, OSError):
        return []


    root = tree.getroot()

    # Initialiser la liste
    items = []

    # Recuperer les categories generales
    global_categories = set(element.text.strip() for element in root.iterfind("./channel/category"))

    # Chercher pour tous les sous-éléments "item"
    for item in root.findall(".//item"):

        # Recuperer l'identifiant
        id = item.findtext("link", default="No link")

        # Recuperer le titre
        raw_title = item.findtext("title", default="No title")
        # Retirer les eventuelles balises html
        title = html.fromstring(raw_title).text_content() if raw_title else "No title"

        # Recuperer le texte brut des descriptions
        raw_description = item.findtext("description", default="No description")
        # Retirer les eventuelles balises html
        description = html.fromstring(raw_description).text_content() if raw_description else "No description"

        # Recuperer la date
        raw_date = item.findtext("pubDate", default="No date")
        date = html.fromstring(raw_date).text_content() if raw_date else "No date"

        # Recuperer les categories spécifiques à l'article
        local_categories = global_categories.copy()
        for category_element in item.iterfind("category"):
            local_categories.add(category_element.text)
    
        items.append({
            "id": id,
            "source": name,
            "title": title,
            "description": description,
            "date": date,
            "categories": sorted(local_categories)
        })

    return items

# R3 les fonctions avec ex1 et ex2
def rss_reader_r3(fichier):
    # Créer la liste pour contenir des éléments du fichier sous forme de dict
    items = []
    # Analyser le fichier xml en utilisant feedparser
    item_feed = feedparser.parse(fichier)
    channel_feed = item_feed.feed
    for entry in item_feed.entries:
        # Stocker des éléments de chaque item ou channel
        categories =  [tag.term for tag in entry.get('tags', [])]
        channel_categories = channel_feed.get('category')
        # 'catégories' est extraite de l'élément par défaut. Si 'channel' contient des catégories, les ajouter aux catégories.
        if channel_categories :
            categories += [channel_categories]

        item = {
            'id': entry.link,
            'source': fichier,
            'title': entry.title,
            'description': entry.description,
            'date': entry.published,
            # Toutes les catégories se trouvent dans entry.tag, mais cela contient d'autres éléments. Donc, en utilisant '.get' pour extraire précisément le contenu.
            # Retour une liste vide si aucune catégorie n'est trouvée
            'categories': categories
        }
        items.append(item)
    return items

"""
Créer une fonction pour chercher et traiter des fichier xml présents dans le répertoire et sous-répertoire.
Utiliser 'os.path.isdir' pour vérifier si le chemin est un répertoire valide.
"""
def parcourir_dossier(adr_dossier):
    items_tous = []
    xml_trouve = False
    # Indicateur pour savoir si des fichiers xml existent

    # Parcourir le répertoire pour traiter directement les fichiers XML qu'il contient
    for element in os.listdir(adr_dossier):
        if element.lower().endswith('.xml'):
            xml_trouve = True
            chemin_complet = os.path.join(adr_dossier, element)
            items = rss_reader_r3(chemin_complet)
            items_tous.extend(items)

    # S'il n'y a pas de fichier xml dans le répertoire, parcourir dans chaque sous-répertoire,
    # jusqu'à en trouver, puis afficher le résultat.
    if not xml_trouve:
        for element in os.listdir(adr_dossier):
            chemin_complet = os.path.join(adr_dossier, element)
            if os.path.isdir(chemin_complet):
                # Répéter, jusqu'à trouver des fichier xml
                items_tous.extend(parcourir_dossier(chemin_complet))

    return items_tous


# La fonction ex2r2
def find_xml_glob(directory_path: str | Path) -> list[Path]:
    """
    Récupère tous les fichiers XML dans un dossier, y compris dans ses sous-dossiers.

    :param directory_path: Chemin du dossier à explorer.
    :return: Liste de fichiers XML trouvés dans le dossier et ses sous-dossiers.
    """
    directory = Path(directory_path)

    # Gerer les erreurs
    if not directory.exists() or not directory.is_dir():
        print(f"Erreur : Le dossier '{directory_path}' n'existe pas ou n'est pas un dossier valide.")
        return []

    # Trouver tous les fichiers XML dans l'arborescence du dossier
    xml_files = list(directory.glob("**/*.xml"))

    return xml_files


# La fonction main
def main():
    # Choisir l'une des trois méthodes
    print("Choisissez la méthode de lecture de flux RSS:")
    print("1: Utiliser le module re")
    print("2: Utiliser le module etree")
    print("3: Utiliser le module feedparser")
    method = input("Votre choix (taper 1/2/3): ").strip()
    # Entrer manuellement le nom du fichier xml
    file_path = input("Le nom du fichier xml: ").strip()
    
    # Initialiser une liste pour stocker tous les items
    all_items = []

    if method == "1":
        items = process_directory(file_path)

    elif method == "2":
        files = find_xml_glob(file_path)
        if not files:
            print("Aucun fichier XML trouvé dans le dossier spécifié.")
            return
        else:
            for file in files:
                items = read_rss_etree(file)
                all_items.extend(items)
        

    elif method == "3":
        items = parcourir_dossier(file_path)
    else:
        print("Choix invalide.")
        return

    if not items:
        print("Aucun article trouvé.")
    else:
        for item in items:
            print(f"id : {item['id']}")
            print(f"source : {item.get('source')}")
            print(f"title : {item['title']}")
            print(f"description : {item['description']}")
            print(f"date : {item['date']}")
            print(f"categories : {item['categories']}")
            print()

if __name__ == "__main__":
    main()
