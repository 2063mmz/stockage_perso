from lxml import etree, html

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

if __name__ == "__main__":
    rss_items = read_rss_etree("Elucid -.xml")
    for item in rss_items:
        print(item)
