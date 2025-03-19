import xml.etree.ElementTree as ET
from pathlib import Path
import glob
from typing import List, Dict, Set
import html

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

def read_xml_files_r2(corpus_dir: str, keywords: List[str]) -> List[Dict]:
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

def remove_duplicates_r2(articles: List[Dict]) -> List[Dict]:
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

def write_data_to_txt(data: List[Dict], output_file: str):
    """
    Écrire les articles filtrés dans un fichier texte.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"id : {item['id']}\n")
            f.write(f"Titre : {item['titre']}\n")
            f.write(f"Source : {item['source']}\n")
            f.write(f"Description : {item['description']}\n")
            f.write(f"Date : {item['date']}\n")
            f.write(f"Catégories : {', '.join(item['categories'])}\n")
            f.write("\n")
    print(f"Données enregistrées dans {output_file}")

def main():
    print("**Filtrage d'articles XML**")
    
    # Demander à l'utilisateur le dossier contenant les fichiers XML
    while True:
        corpus_dir = input("Entrez le chemin du dossier contenant les fichiers XML : ").strip()
        if Path(corpus_dir).exists() and Path(corpus_dir).is_dir():
            break
        else:
            print("Chemin invalide. Veuillez entrer un dossier valide.")

    # Demander à l'utilisateur de saisir les mots-clés séparés par un espace
    keywords = input("Entrez un ou plusieurs mots-clés (séparés par un espace) : ").strip().split()

    if not keywords:
        print("Aucun mot-clé fourni.")
        return

    # Lire les fichiers XML et filtrer les articles
    articles = read_xml_files_r2(corpus_dir, keywords)

    # Supprimer les articles doublés
    unique_articles = remove_duplicates_r2(articles)

    if not unique_articles:
        print("Aucun article après suppression des doublons.")
        return

    # Demander à l'utilisateur où enregistrer le fichier contenant les résultats
    while True:
        output_dir = input("Entrez le chemin du dossier où vous souhaitez enregistrer 'filtrage.txt' : ").strip()
        if Path(output_dir).exists() and Path(output_dir).is_dir():
            break
        else:
            print("Chemin invalide. Veuillez entrer un dossier valide.")

    # Déterminer le chemin complet du fichier de sortie
    output_file = Path(output_dir) / "filtrage.txt"

    # Sauvegarde dans 'filtrage.txt'
    write_data_to_txt(unique_articles, output_file)

if __name__ == "__main__":
    main()
