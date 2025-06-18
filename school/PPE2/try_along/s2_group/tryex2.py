import thulac
import os
import re
import sys
from typing import List

###########################################################
# script r1
###########################################################

dossier="./Corpus" # Faites attention au repertoire que vous éxécutez le programme
thu = thulac.thulac(seg_only=True)#import thulac pour segmenter les mots chinois et les phrases sans espace
def seg_mots_chinois(text):
    
    def segment_chinese(match):
        
        return thu.cut(match.group(), text=True) 
    
    
    return re.sub(r"[\u4e00-\u9fff]+", segment_chinese, text)

def lire_corpus(dossier): # Lire les textes
    if not os.path.isdir(dossier):
        print(f"le dossier '{dossier}' n'existe pas.")
        return []
    
    contenus = [] # Créer la liste de chaînes
    for fichier in os.listdir(dossier):
        chemin_fichier = os.path.join(dossier,fichier)

        if os.path.isfile(chemin_fichier):
            try:
                with open(chemin_fichier,"r",encoding="utf-8") as f:
                    text = f.read()
                    contenus.append(re.sub(r"[^\u00C0-\u017F\u4e00-\u9fff\uac00-\ud7afa-zA-Z'']+|([a-zA-Z]\.[a-zA-Z])", " ", text)) # CY: ajouter replace pour remplacer \n dans les listes a la fin
            except Exception as e:
                print(f"Erreur lors de la lecture de {fichier}: {e}")

    return contenus

corpus_texts = lire_corpus(dossier)
print(corpus_texts)
print(f"Nombre de fichiers lus : {len(corpus_texts)}")


def mots_fichier_count(mots_list, dossier):
    # Un dictinnaire vide pour compter chaque mot au nombre de documents  dans lequel il apparaît
    count_dic = {mots: 0 for mots in mots_list}  
    # Un dictionnaire vide pour stocker la regex correspondant à chaque mot
    patterns = {} 
    n_mots_list = list(set(mots_list)) # Supprimer les doublons de la liste de mots

    for mots in n_mots_list:
        # Regex utilise '\b' pour délimiter les bords du mot et ignore majuscules et minu
        patterns[mots] = re.compile(r'\b' + re.escape(mots) + r'\b', re.IGNORECASE)
    for nom_f in os.listdir(dossier):
        fichiers = f"{dossier}/{nom_f}"  # Chemin complet du fichier
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

mots_list = corpus_texts
print(mots_fichier_count(mots_list, dossier))

###########################################################
# etape 2 combination
###########################################################



