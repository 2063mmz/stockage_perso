import pickle
import argparse
import os
from pathlib import Path
from typing import List

def save_pickle(xml_files: List[str], output_file: Path) -> None:
    # Écrire les fichier xml en format binaire dans out_put pour le sauvegarder
    with open(output_file, "wb") as f:  
        pickle.dump(xml_files, f)

def load_pickle(input_file: Path) -> List[str]:
    # Désérialiser les données et les reconstruit sous forme de liste
    with open(input_file, "rb") as f:
        return pickle.load(f)

def get_files(corpus_dir: str) -> List[str]:
    filepath = []
    try:
        files = os.listdir(corpus_dir)
    except FileNotFoundError:
        print(f"Le chemin spécifié n'est pas un dossier valide : {corpus_dir}")
        return []

    for filename in files:
        full_path = os.path.join(corpus_dir, filename)
        if os.path.isfile(full_path) and filename.lower().endswith('.xml'):
            filepath.append(full_path)
        elif os.path.isdir(full_path):
            filepath.extend(get_files(full_path))

    return filepath

def main():
    parser = argparse.ArgumentParser(description="Sérialiser le corpus xml en Pickle")
    parser.add_argument("corpus_dir", type=str, help="contenir le corpus xml")
    parser.add_argument("output_pickle", nargs="?", type=str, help="fichier de sortie (optionnel)")

    args = parser.parse_args()

    corpus_dir = args.corpus_dir

    # output_pickle est un chemin sous forme de lst
    if args.output_pickle is None:
        output_pickle = "corpus.pkl"
    else:
        output_pickle = args.output_pickle 

    xml_fichiers = get_files(corpus_dir)
    if not xml_fichiers:
        print("Aucun fichier XML trouvé.")
        return

    save_pickle(xml_fichiers, output_pickle) 
    print(f"Les informations ont été enregistrées {output_pickle}")

if __name__ == "__main__":
    main()