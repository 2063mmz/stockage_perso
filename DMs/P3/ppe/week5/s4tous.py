import xml.etree.ElementTree as ET
from pathlib import Path
import glob
import datetime
from typing import List, Dict, Set, Callable

# -------------------------------
# 读取所有XML文件并解析文章
# -------------------------------
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
            tree = ET.parse(xml_file)
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
        except Exception as e:
            print(f"Erreur de lecture {xml_file}: {e}")

    return all_articles

# -------------------------------
# 去除重复文章
# -------------------------------
def remove_duplicates_r2(articles: List[Dict]) -> List[Dict]:
    """
    Supprimer les articles en double en utilisant 'titre + description' comme clé.
    """
    seen: Set[str] = set()
    unique_articles = []

    for article in articles:
        unique_key = f"{article.get('titre','')}|{article.get('description','')}"
        if unique_key not in seen:
            seen.add(unique_key)
            unique_articles.append(article)

    return unique_articles

# -------------------------------
# 写入结果到文本文件
# -------------------------------
def write_data_to_txt(data: List[Dict], output_file: str):
    """
    Écrire les articles filtrés dans un fichier texte.
    """
    with open(output_file, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(f"id : {item.get('id','')}\n")
            f.write(f"Titre : {item.get('titre','')}\n")
            f.write(f"Source : {item.get('source','')}\n")
            f.write(f"Description : {item.get('description','')}\n")
            f.write(f"Date : {item.get('date','')}\n")
            f.write(f"Catégories : {', '.join(item.get('categories', []))}\n")
            f.write("\n")
    print(f"Données enregistrées dans {output_file}")

# -------------------------------
# 过滤器：返回一个过滤函数（类别）
# -------------------------------
def create_filter_categorie(categorie_choisie: str) -> Callable[[dict], bool]:
    def filtre(item: dict) -> bool:
        categories = item.get('categories', [])
        return categorie_choisie.lower() in [c.lower() for c in categories]
    return filtre

# -------------------------------
# 过滤器：基于日期的过滤（支持多种格式）
# -------------------------------
def filtre_r1(item: dict, date_debut=None, date_fin=None) -> bool:
    """
    Filtre les articles en fonction de leur date de publication.
    """
    if 'date' not in item or not item['date']:
        return False
    date_formats = [
        '%a, %d %b %Y %H:%M:%S %z',  # RFC 822/1123 format
        '%a, %d %b %Y %H:%M:%S %Z',
        '%a, %d %b %Y %H:%M:%S',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%Y-%m-%d %H:%M:%S',
        '%d %b %Y %H:%M:%S',
        '%a %b %d %H:%M:%S %Y',
    ]
    date_article = None
    try:
        for fmt in date_formats:
            try:
                date_article = datetime.datetime.strptime(item['date'], fmt)
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

# -------------------------------
# 过滤器：返回一个过滤函数（来源）
# -------------------------------
def create_filter_source(source_choisie: str) -> Callable[[dict], bool]:
    def filtre(item: dict) -> bool:
        return source_choisie.lower() in item.get("source", "").lower()
    return filtre

# -------------------------------
# 通用过滤函数：应用多个过滤器
# -------------------------------
def filtrage(filtres: List[Callable[[dict], bool]], articles: List[dict]) -> List[dict]:
    resultat = []
    for article in articles:
        if all(f(article) for f in filtres):
            resultat.append(article)
    return resultat

# -------------------------------
# 主函数：整合处理和过滤
# -------------------------------
def main():
    print("**Filtrage d'articles XML avec filtres par catégorie, date et source**")
    
    # 1. 获取存放 XML 文件的文件夹路径
    while True:
        corpus_dir = input("Entrez le chemin du dossier contenant les fichiers XML : ").strip()
        if Path(corpus_dir).exists() and Path(corpus_dir).is_dir():
            break
        else:
            print("Chemin invalide. Veuillez entrer un dossier valide.")

    # 2. 输入用于筛选文件名的关键词（可多个）
    keywords = input("Entrez un ou plusieurs mots-clés (séparés par un espace) : ").strip().split()
    if not keywords:
        print("Aucun mot-clé fourni.")
        return

    # 3. 读取并解析所有匹ements XML
    articles = read_xml_files_r2(corpus_dir, keywords)

    # 4. 去除重复文章
    unique_articles = remove_duplicates_r2(articles)
    if not unique_articles:
        print("Aucun article après suppression des doublons.")
        return

    # 5. 提示用户输入过滤条件
    categorie_input = input("Filtrer par catégorie (laisser vide pour ne pas filtrer par catégorie) : ").strip()
    date_debut_input = input("Filtrer par date - date de début (YYYY-MM-DD, laisser vide si non) : ").strip()
    date_fin_input = input("Filtrer par date - date de fin (YYYY-MM-DD, laisser vide si non) : ").strip()
    source_input = input("Filtrer par source (laisser vide pour ne pas filtrer par source) : ").strip()

    # 构造过滤函数列表
    filtres: List[Callable[[dict], bool]] = []

    if categorie_input:
        filtres.append(create_filter_categorie(categorie_input))
    if date_debut_input or date_fin_input:
        date_format = '%Y-%m-%d'
        date_debut = datetime.datetime.strptime(date_debut_input, date_format) if date_debut_input else None
        date_fin = datetime.datetime.strptime(date_fin_input, date_format) if date_fin_input else None
        # 这里使用lambda包装filtre_r1，使其符合Callable[[dict], bool]格式
        filtres.append(lambda item: filtre_r1(item, date_debut, date_fin))
    if source_input:
        filtres.append(create_filter_source(source_input))

    # 如果设置了过滤条件，则应用过滤
    if filtres:
        articles_filtres = filtrage(filtres, unique_articles)
    else:
        articles_filtres = unique_articles

    if not articles_filtres:
        print("Aucun article ne correspond aux critères de filtrage.")
        return

    # 6. 写入过滤后的结果到文件 "filtrage.txt"
    output_file = "filtrage.txt"
    write_data_to_txt(articles_filtres, output_file)

if __name__ == "__main__":
    main()


#######################################################################
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

def filtre_r3(categorie_choisie: str) -> Callable[[dict], bool]:
    def filtre(item: dict) -> bool:
        categories = item.get('categories', [])
        # Comparaison insensible à la casse
        return any(categorie_choisie.lower() == cat.lower() for cat in categories)
    return filtre


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
    parser.add_argument("directory", type=str, help="Directory containing RSS files")
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

    for file in files:
        res = reader_funcs[choix][3](file)
        if not res:
            print(f"Pour le ficher {file}, aucune information n'a été trouvée.")

    # Run Filter: catecories
    # Corr: ajouter '.strip()' pour supprimer les espaces des deux côtés d'un input
    categorie_choisie = input("Entrez une catégorie d'article :").strip()

    # Générer le filtre à partir de la catégorie saisie
    filter_func = filtre_r3(categorie_choisie)

    # Traitement des fichiers
    rss_files = [f for f in files if os.path.isfile(os.path.join(args.directory, f))]
    for filename in rss_files:
        filepath = os.path.join(args.directory, filename)
        print(f"Traitement du fichier {filepath}")

        metadata = rss_reader_r3(filepath)
        if not metadata:
            print(f"Rien dans {filepath}")
            continue

        res = [item for item in metadata if filter_func(item)]


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

