'''
La fonction 'rss_reader_r3' n'est pas exactement la même que celle de l'ex1.
Il y a quelques modifications, ajouter qqn conditions.
'''
# Importation les modules feedparser et os
import feedparser
import os

'''
 La paramètre de la fonction ont été modifiées, car dans la fonction main,
 elle est déjà obtenu le chemin complet du fichier à traiter.
 Donc, os.path.join n'est pas nécessaire dans cette fonction.
'''
def rss_reader_r3(adr_fichs):
    # Créer la liste pour contenir des éléments de chaque fichier sous forme de dict
    items = []
    # Traiter directement
    feed = feedparser.parse(adr_fichs)
    for entry in feed.entries:
        # Stocker des éléments de chaque item
        item = {
            'id': entry.link,
            'source': os.path.basename(adr_fichs),
            'title': entry.title,
            'description': entry.description,
            'date': entry.published,
            # Toutes les catégories se trouvent dans entry.tag, mais cela contient d'autres éléments. Donc, en utilisant '.get' pour extraire précisément le contenu.
            # Retour une liste vide si aucune catégorie n'est trouvée
            'categories': [tag.term for tag in entry.get('tags',[])]
        }
        items.append(item)
    return items

def main():
    # Ici, il faut taper un nom de chemin
    adr = input("Veuillez entrer l'adresse du corpus: ")
    '''
    Créer une boucle pour vérifier si l'adresse est correcte et si des dossiers existe
    'os.path.isdir' en utilisant pour vérifier si le chemin est un répertoire valide
    '''
    while not os.path.isdir(adr):
        print(f"{adr} n'est pas un dossier valide!")
        # Si n'est pas valide, taper un nouveau chemin ou quiter
        adr_nouv = input(f"\nEntrez un nouveau chemin(ou 'q' pour quiter ):")
        if adr_nouv == 'q':
            exit()
        if os.path.isdir(adr_nouv):
            adr = adr_nouv
        else:
            print("chemin invalide")
    '''
    Créer une boucle pour vérifier si le répertoire contient des fichiers xml ou des dossiers.
    S'il n'y a pas de fichiers xml, continuer à ouvrir des dossiers.
    '''
    while True:
        # Une liste vide pour stocker tous les items.
        items_tous = []
        # Si ce répertoire contient des fichiers xml, traiter
        for fichier in os.listdir(adr):
            if fichier.lower().endswith('.xml'):
                adr_fich = os.path.join(adr, fichier)
                items = rss_reader_r3(adr_fich)
                for item in items:
                    print(f"ID : {item['id']}")
                    print(f"Source : {item['source']}")
                    print(f"Title : {item['title']}")
                    print(f"Description : {item['description']}")
                    print(f"Date : {item['date']}")
                    print(f"Categories : {item['categories']}")
                    print()
                items_tous.extend(items)
        # Si des résultats sont obtenus, on break
        if items_tous:
            break
        # Si il n'exist pas des fichiers xml, on continue de chercher et ouvrir nouveau dossier
        print("Aucun fichier xml, continuer ('c') ou quitr('q'):")
        print("Voici le contenu:",os.listdir(adr))
        # Taper ton choix
        a = input("Choisir un dossier:")
        if a == 'q':
            exit()
        # Comme la boucle de presetant, trouver des dossiers ou rien dans un nouveau chemin
        adr_nouv = os.path.join(adr, a)
        if os.path.join(adr_nouv):
            adr = adr_nouv
        else:
            print("Chemin invalide!")


if __name__ == '__main__':
    main()
