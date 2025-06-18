import os
import re
import sys
from lxml import etree, html
import feedparser

# R1
def read_rss_with_re(file_path):

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Erreur : Le fichier '{file_path}' n'existe pas.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors de la lecture du fichier : {e}")
        sys.exit(1)

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



#R2
def read_rss_etree(file_path: str)->list[dict[str, str]]:
    """
    Lit un fichier XML RSS et retourne les items avec leur texte et métadonnées.

    :param file: Chemin du fichier à traiter.
    :return: Texte et métadonnées du fichier.
    """
    tree = etree.parse(file_path)
    root = tree.getroot()

    # Chercher tous les sous-éléments "title" qui sont des enfants de l'élément "channel"
    source = root.findtext(".//channel/title", default="Unknown source") + ".xml"

    items = []
    # Chercher pour tous les sous-éléments "item"
    for item in root.findall(".//item"):
        id = item.findtext("link", default="No link")
        title = item.findtext("title", default="No title")
        # Extraire le texte brut des descriptions
        raw_description = item.findtext("description", default="No description")
        # Retirer les balises html de la description
        description = html.fromstring(raw_description).text_content() if raw_description else "No description"
        date = item.findtext("pubDate", default="No date")
        categories = [category.text for category in item.findall("category") if category.text]

        items.append({
            "id": id,
            "source": source,
            "title": title,
            "description": description,
            "date": date,
            "categories": categories
        })

    return items
    


# R3
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


def main():
    # Choisir l'une des trois méthodes
    print("Choisissez la méthode de lecture de flux RSS:")
    print("1: Utiliser le module re")
    print("2: Utiliser le module etree")
    print("3: Utiliser le module feedparser")
    method = input("Votre choix (taper 1/2/3): ").strip()
    # Entrer manuellement le nom du fichier xml
    file_path = input("Le chemin ou le nom du fichier xml: ").strip()

    if method == "1":
        items = read_rss_with_re(file_path)

    elif method == "2":
        items = read_rss_etree(file_path)
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
