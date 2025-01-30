#!/bin/bash

## vérifier si le fichier est bien fourni.
if [ -z "$1" ]; then
    echo "Sans argument!"
    exit 1
fi

## lier le fichier
URL="$1"

## créer ces deux dosiers dans le chemin actuel
## mkdir -p aspirations dumps_text

## initialiser le compteur
num=1

## parcourir la liste des URL
while read url;
do
    # ignorer les lignes vides
    if [ -z "$url" ];
    then
        continue
    fi

## générer le nom du fichier
    nom_fichier="lang1-$num"
    ((num++))

    ## télécharger le fichier HTML
    ## essayer d'utiliser '-b' pour résoudre le problème des cookies, mais pas réussir
    curl -s -L "$url" -o "/home/caoyue/PPE_github/groupePPE1_2024/aspirations/$nom_fichier.html"

    ## extraire le contenu texte, en utilisant sed
    lynx -dump -nolist -width=200 "$url" | sed "s/|//g; s/\[.*\]//g; s/\*//g; s/+//g; s/_//g; /^$/d" > "/home/caoyue/PPE_github/groupePPE1_2024/dumps-text/$nom_fichier.txt"

    # afficher les informations d'état
    echo "Processed: $url -> aspirations/$nom_fichier.html, dumps-text/$nom_fichier.txt"
done < "$URL"

