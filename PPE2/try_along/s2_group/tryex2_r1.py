import thulac
import os
import re
import sys
from typing import List

###########################################################
# script r1
###########################################################

dossier="./Corpus" # Faites attention au repertoire que vous éxécutez le programme
# thu = thulac.thulac(seg_only=False) #import thulac pour segmenter les mots chinois et les phrases sans espace
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
                    contenus.append(re.sub(r"[^\u00C0-\u017F\u4e00-\u9fff\uac00-\ud7afa-zA-Z'’]+|([a-zA-Z]\.[a-zA-Z])", " ", text)) # ajouter replace pour remplacer \n dans les listes a la fin
            except Exception as e:
                print(f"Erreur lors de la lecture de {fichier}: {e}")

    return contenus

corpus_texts = lire_corpus(dossier)
print(corpus_texts)
print(f"Nombre de fichiers lus : {len(corpus_texts)}")


