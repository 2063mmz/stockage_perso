def dico_occurences_mots(liste):


	corpus = " ".join(liste) #Pour mettre tout les textes du corpus bout à bout

	mots = corpus.split() #Pour séparer les mots (sinon ça prend tout en compte)

	occurences = {} #Initialisation du dictionnaire

	for mot in mots:
		if mot in occurences:
			occurences[mot] += 1 #Si le mot est déjà dans le dictionnaire il ajoute +1 à son compteur

		else:
			occurences[mot] = 1 #Si le mot n'est pas dans le dictionnaire, il est ajouté avec un compte de 1



	return occurences_mots

liste= []