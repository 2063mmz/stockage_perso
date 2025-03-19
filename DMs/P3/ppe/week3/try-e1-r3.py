# Importation la module feedparser
import feedparser

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

def main():
    # Résultat optional, il y a 2, soit avec un fichier absolus, soit taper un nom du fichier 
    # fichier = 'Flux RSS - BFM BUSINESS - Entreprises - Energie.xml'
    fichier = input('Choisir un fichier pour traiter:')
    items = rss_reader_r3(fichier)
    for item in items:
        print(f"id : {item['id']}")
        print(f"source : {item['source']}")
        print(f"title : {item['title']}")
        print(f"description : {item['description']}")
        print(f"date : {item['date']}")
        print(f"categories : {item['categories']}")
        print()

if __name__ == '__main__':
    main()



