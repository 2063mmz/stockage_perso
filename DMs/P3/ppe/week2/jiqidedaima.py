import thulac
import os
import re
import sys
from typing import List


dossier="./Corpus" # Faites attention au repertoire que vous éxécutez le programme
thu = thulac.thulac(seg_only=True)#import thulac pour segmenter les mots chinois et les phrases sans espace
# CY:Écrire une fonction qui peut segmenter les chinois, pour le problème de l'absence d'espaces entre les mots chinois
def seg_mots_chinois(text):
    # Segmentation les parties en chinois
    def segment_chinese(match):
        
        return thu.cut(match.group(), text=True)  # Permet d'afficher le résultat sous forme string

    # Segmentation que pour les parties en chinois'[\u4e00-\u9fff]', en laissant les autres
    return re.sub(r"[\u4e00-\u9fff]+", segment_chinese, text)

###########################################################
# script r1
###########################################################

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
                    clair_text = re.sub(r"[^\u00C0-\u017F\u4e00-\u9fff\uac00-\ud7afa-zA-Z'’.]", " ", text)
                    contenus.append(clair_text) # CY: ajouter replace pour remplacer \n dans les listes a la fin
            except Exception as e:
                print(f"Erreur lors de la lecture de {fichier}: {e}")

    return contenus

corpus_texts = lire_corpus(dossier)
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

def mots_fichier_count(mots_list, dossier):
    n_mots_list = set(m.lower() for m in mots_list) # Supprimer les doublons de la liste de mots
    
    # Un dictinnaire vide pour compter chaque mot au nombre de documents  dans lequel il apparaît
    count_dict = {mot: 0 for mot in n_mots_list}  
    
    
    for nom_f in os.listdir(dossier):
        fichiers = os.path.join(dossier, nom_f)  # Chemin complet du fichier
            # Ouvrir le fichier, si les caractères non reconnus, on les ignore
        with open(fichiers, 'r', encoding='utf-8', errors='ignore') as f:
            text = seg_mots_chinois(f.read()).lower()
            n_mots = set(text.split())
            for mot in n_mots & n_mots_list:
                count_dict[mot] += 1
            

    return count_dict


###########################################################
# main: exécuter les trois scripts
###########################################################

def main():
    # 1) Lire le corpus
    corpus_texts = lire_corpus(dossier)
    
    # 2) Obtenir les occurrences brutes
    occurence_mots = dico_occurences_mots(corpus_texts)

    dict_mots_docs = mots_fichier_count(occurence_mots.keys(), dossier)


    with open("resultats.tsv", "w", encoding="utf-8") as f:
        f.write("MOT\tOCCURRENCES\tNombre_de_documents\n")
        # 按照词的字典序进行排序
        for mot in sorted(occurence_mots.keys()):
            freqence = occurence_mots[mot]
            doc_count = dict_mots_docs.get(mot, 0)
            f.write(f"{mot}\t{freqence}\t{doc_count}\n")

    

    print(f"Le fichier resuletas a été créé.")

    # Afficher le résultat final
    # print("mot\tle nombre d’occurrences total\tle nombre de documents")
    # print()
    # for mot in dico_mots_docs.keys():
    #    print(f"{mot}\t{dico_occu_mots[mot]}\t{dico_mots_docs[mot]}")

if __name__ == "__main__":
    main()