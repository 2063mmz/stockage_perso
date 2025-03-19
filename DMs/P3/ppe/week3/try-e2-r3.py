
# Importation des modules feedparser et os
import feedparser
import os


def rss_reader_r3(fichier):
    # Créer la liste pour contenir des éléments de chaque fichier sous forme de dict
    items = []
    # Traiter directement 
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
            for item in items:
                print(f"ID : {item['id']}")
                print(f"Source : {item['source']}")
                print(f"Title : {item['title']}")
                print(f"Description : {item['description']}")
                print(f"Date : {item['date']}")
                print(f"Categories : {item['categories']}")
                print()
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
    # Définir le chemin du corpus, et assurer il existe dans le répertoire actuel
    adr_dossier = "2025" 
    
    # Sortir les resultats
    resultats = parcourir_dossier(adr_dossier)
    print("Traitement terminé.")
    return resultats

if __name__ == '__main__':
    main()