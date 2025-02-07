import os
import re

def mots_fichier_count(mots_list, adresse_f):
    # Un dictinnaire vide pour compter chaque mot au nombre de documents  dans lequel il apparaît
    count_dic = {mots: 0 for mots in mots_list}  
    # Un dictionnaire vide pour stocker la regex correspondant à chaque mot
    patterns = {} 
    n_mots_list = list(set(mots_list)) # Supprimer les doublons de la liste de mots

    for mots in n_mots_list:
        # Regex utilise '\b' pour délimiter les bords du mot et ignore majuscules et minu
        patterns[mots] = re.compile(r'\b' + re.escape(mots) + r'\b', re.IGNORECASE)
    for nom_f in os.listdir(adresse_f):
        fichiers = f"{adresse_f}/{nom_f}"  # Chemin complet du fichier
        # Si le chemin est vide, on passe
        if not fichiers: 
            continue
        # Ouvrir le fichier, si les caractères non reconnus, on les ignore
        with open(fichiers, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
            for mots in mots_list:
                # Si le regex associée au mot trouve une correspondance dans le texte, plus 1
                if patterns[mots].search(text):
                    count_dic[mots] += 1
    return count_dic

adresse_f = './Corpus'

print(mots_fichier_count(mots_list, adresse_f))

