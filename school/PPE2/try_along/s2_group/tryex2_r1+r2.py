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

###########################################################
# script r2
###########################################################

def dico_occurences_mots(liste):
    corpus = " ".join(liste) #Pour mettre tout les textes du corpus bout à bout
    
    corpus = seg_mots_chinois(corpus) # CY: Ajouter le fonction pour segmenter que des mots chinois
    
    mots = corpus.split() #Pour séparer les mots (sinon ça prend tout en compte)
    
    occurences = {} #Initialisation du dictionnaire
    
    for mot in mots:
        if not re.search(r"[a-zA-Z\u4e00-\u9fff\uac00-\ud7af]", mot):
            continue
        if mot in occurences:
            occurences[mot] += 1 #Si le mot est déjà dans le dictionnaire il ajoute +1 à son compteur
        else:
            occurences[mot] = 1 #Si le mot n'est pas dans le dictionnaire, il est ajouté avec un compte de 1
    return occurences

############################


###########################################################
# MAIN : Exécuter tout
###########################################################

def main():
    # 1) Lire le corpus
    liste = lire_corpus(dossier)
    
    # 2) Obtenir les occurrences brutes
    dico_occu_mots = dico_occurences_mots(liste)
    
 
    file_path = "out.txt" 
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("MOT\tOCCURRENCES\n")  # Ajout d'un en-tête
        for mot, count in sorted(dico_occu_mots.items()):
            f.write(f"{mot}\t{count}\n")  # É

    print(f"Le fichier '{file_path}' a été créé et le texte a été écrit avec succès.")

        # 4) Afficher le résultat final
    print("MOT\tOCCURRENCES")
    for mot in sorted(dico_occu_mots.keys()):
        print(f"{mot}\t{dico_occu_mots[mot]}")

if __name__ == "__main__":
    main()
