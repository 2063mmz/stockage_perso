import thulac
import os
import re
import sys
from typing import List
import argparse


dossier="./Corpus" # Faites attention au repertoire que vous éxécutez le programme

thu = thulac.thulac(seg_only=True)# Import thulac pour segmenter les mots chinois et les phrases sans espace


###########################################################
# Definir la facon de lire les fichiers
###########################################################

def my_parser():

    parser = argparse.ArgumentParser(
        description="Ce script permet de lire un corpus de deux façons 'args' ou 'stdin'."
    )
    parser.add_argument("--mode",
                        choices=["args", "stdin"],
                        required=True,
                        help="'args' permettre de lire des fichiers direct."
                             "'stdin' pour l'entrée standard.")
    args = parser.parse_args()
    return args

###########################################################
# stdin
###########################################################

def lire_corpus_stdin():

    liste = []  # Liste pour stocker les fichiers sous forme d'une seule ligne
    texte_courant = ""

    # Lire ligne par ligne
    for line in sys.stdin:
        line = line.strip()
        if line != "":  # Si ce ligne n'est pas vide
            # Remplacer \n dans cette ligne -> une space
            texte_courant += line + " "
        else:
            # Si une ligne vide, on pense que c'est un nouveau fichier
            if texte_courant:
                # Ajouter les textes qui ete bien traite et a la fin de textes avec un '\n'
                liste.append(texte_courant.strip() + "\n")
                # Après parcourir une fois, réinitialiser pour le prochain fichier
                texte_courant = ""

    if texte_courant:
        liste.append(texte_courant.strip() + "\n")

    return liste


###########################################################
# Segmenter le chinois
###########################################################

# CY:Ecrire une fonction qui peut segmenter les chinois, pour le problème de l'absence d'espaces entre les mots chinois
def seg_mots_chinois(text):
    # Segmentation les parties en chinois
    def segment_chinese(match):

        # Permet d'afficher le résultat sous forme string
        return thu.cut(match.group(), text=True)

    # Segmentation que pour les parties en chinois'[\u4e00-\u9fff]', laisser les autres
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

                    # CY: Ajouter regex pour supprimer les symboles spéciaux
                    # mais dans le résultat, ce qui n'est pas entièrement nettoyé :(
                    clair_text = re.sub(r"[^\u00C0-\u017F\u4e00-\u9fff\uac00-\ud7afa-zA-Z'’.]", " ", text)
                    contenus.append(clair_text)
            except Exception as e:
                print(f"Erreur lors de la lecture de {fichier}: {e}")

    return contenus

corpus_texts = lire_corpus(dossier)
print(f"Nombre de fichiers lus : {len(corpus_texts)}")


###########################################################
# script r2
###########################################################

def dico_occurences_mots(liste):

    # CY: Mondifier de " ".join(liste) à (" ".join(liste)).lower() pour mettre tout les mots en minuscules
    corpus = (" ".join(liste)).lower() #Pour mettre tout les textes du corpus bout à bout

    # CY: Ajouter le fonction pour segmenter que des mots chinois dans le corpus
    corpus = seg_mots_chinois(corpus)

    mots = corpus.split() #Pour séparer les mots (sinon ça prend tout en compte)

    occurences = {} #Initialisation du dictionnaire

    for mot in mots:

        # CY: Ajouter une condition pour supprimer les longs symboles spéciaux et rester que les mots
        if not re.search(r"[a-zA-Z\u4e00-\u9fff\uac00-\ud7af]", mot):
            continue

        if mot in occurences:
            occurences[mot] += 1 #Si le mot est déjà dans le dictionnaire il ajoute +1 à son compteur
        else:
            occurences[mot] = 1 #Si le mot n'est pas dans le dictionnaire, il est ajouté avec un compte de 1
    return occurences

###########################################################
# script r3
###########################################################

def mots_fichier_count(mots_list, dossier):
    # Supprimer les doublons de la liste de mots et pour mettre tout les mots en minuscules
    n_mots_list = set(m.lower() for m in mots_list)

    # Un dictinnaire vide pour compter chaque mot au nombre de documents  dans lequel il apparaît
    count_dict = {mot: 0 for mot in n_mots_list}

    # Chemin complet du fichier
    for nom_f in os.listdir(dossier):
        fichiers = os.path.join(dossier, nom_f)

        # Ouvrir le fichier, si les caractères non reconnus, on les ignore
        with open(fichiers, 'r', encoding='utf-8', errors='ignore') as f:
            # Segmenter les mots chinois dans le fichier
            text = seg_mots_chinois(f.read()).lower()
            # Puis les segmenter avec une facon normale
            n_mots = set(text.split())

            # Compter les mots qui dans la liste de sortie et aussi dans le document
            for mot in n_mots_list & n_mots:
                count_dict[mot] += 1
            else:
                continue


    return count_dict


###########################################################
# CY: main
###########################################################

def main():


    # 1, il faut choisi un facon de lecture des fichiers
    parser = my_parser()
    if parser.mode == "stdin":
        corpus_texts = lire_corpus_stdin()
    else:
        corpus_texts = lire_corpus(dossier)

    # Script r2
    occurence_mots = dico_occurences_mots(corpus_texts)

    # Script r3
    dict_mots_docs = mots_fichier_count(occurence_mots.keys(), dossier)

    # Ecrire directement dans un fichier TSV pour sauvegarder facilement
    with open("Extraction_du_lexique.tsv", "w", encoding="utf-8") as f:
        # Les titres
        f.write("Mot\tOccurence\tNB_de_documents\n")

        # Trier avec l'ordre du dictionaire
        for mot in sorted(occurence_mots.keys()):
            # Les résultats de r2
            frequence = occurence_mots[mot]
            # Compter
            doc_compte = dict_mots_docs.get(mot, 0)
            f.write(f"{mot}\t{frequence}\t{doc_compte}\n")



    print(f"Le fichier resuletas a été créé")

if __name__ == "__main__":
    main()
