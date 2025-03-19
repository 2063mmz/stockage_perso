import os
import feedparser
from datetime import datetime
from email.utils import parsedate_to_datetime

# La fonction s3ex2r3 que j'ai écrite
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


# Cette fonction pour filtrer la date des articles dans un fichier xml
def filtrage_date(elements_items, date_debut, date_fin):
    # Créer une liste vide pour stocker les éléments qui remplissent les conditions
    filtrage_items = []

    for element in elements_items:
        # D'abord, extraire le str de date, et puis utiliser 'parsedate_to_datetime' pour renvoie un datetime,
        # et utiliser '.date' pour extraire uniquement la date JJ/MM/YYYY
        pub_date = parsedate_to_datetime(element['date']).date()
        
        # Si la date est antérieure/postérieure à la date de début/fin, marquer invalide
        valid = True
        if date_debut and pub_date < date_debut:
            valid = False
        if date_fin and pub_date > date_fin:
            valid = False
            
        if valid:
            filtrage_items.append(element)

    return filtrage_items

def main():
    # Obtenir le chemin 
    dossier = input("Le chemin du dossier:")
    fichiers = [os.path.join(dossier, f) for f in os.listdir(dossier)]

    # Obtenir les dates
    debut_input = input("Taper la date de début (JJ/MM/YYYY):").strip()
    fin_input = input("Taper la date de fin (JJ/MM/YYYY):").strip()
    
    try:
        # Utiliser datetime.strptime et renvoie une classe datetime correspondant à date_string, analysée selon format
        if debut_input:
            date_debut = datetime.strptime(debut_input, "%d/%m/%Y").date()
            
        if fin_input:
            date_fin = datetime.strptime(fin_input, "%d/%m/%Y").date()
    
    # Lorsque les conditions ne sont pas remplies, le résultat renverra ValueError         
    except ValueError as Erreur:
        print(f"Format incorrect {Erreur}")
        return
    
    # Traiter tous les fichiers xml
    elements_items = []
    for fichier in fichiers:
        elements_items.extend(rss_reader_r3(fichier))

    resultats = filtrage_date(elements_items, date_debut, date_fin)
    
    print(f"\nTrouver {len(resultats)} articles correspondants：")
    count = 1
    for item in resultats:
            print(f"{count}. {item['title']}")
            count += 1

if __name__ == "__main__":
    main()