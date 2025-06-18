import thulac
import os
import re
import sys
from typing import List
import argparse
from tabulate import tabulate


def lire_corpus_stdin():

    liste = []  # Liste pour stocker les fichiers sous forme d'une seule ligne
    texte_courant = ""  
    contenue = []
    tout = sys.stdin.read()
    # Lire ligne par ligne
    for line in tout.splitlines():  
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
    # Pour le dernier fichier (Car le dernier n'ai pas un linge vide)   
    if texte_courant:  
        liste.append(texte_courant.strip() + "\n")
    
    for mot in liste:
        clair_text = re.sub(r"[^\u00C0-\u017F\u4e00-\u9fff\uac00-\ud7afa-zA-Z'’.]", " ", mot)
        contenue.append(clair_text)

    return contenue

print(lire_corpus_stdin())
