import csv
import json
from collections import defaultdict
from Utils import separator #Définir votre propre séparateur Ex: '\t', ' '

#/\/\/\/\/\/\ Nom de la métrique: Croisements /\/\/\/\/\/\
# Le but de cette métrique est d'identifier les cellules où circulent le plus d'utilisateurs.

##############################
# --- Taille des cellules ---#
##############################
size = 2
#  4 : cellule au mètre
#  3 : cellule à la rue
#  2 : cellule au quartier
#  1 : cellule à la ville
#  0 : cellule à la région Française
# -1 : cellule au pays

#############################################################
# --- Pourcentage de cellule les plus visités à vérifier ---#
#############################################################
pt = 0.1
# 0.5: 10% des cellules les plus visités doivent être présente dans 10% des cellules du
# fichier anonymisé.

def main(originalFile, anonymisedFile, parameters=None):
	#Define global variable
	if parameters is None:
		parameters = {"size":2, "pt":0.1}

	global size
	size = parameters.get("size", 3)
	global pt
	pt = parameters.get("pt", 0.2)

	#Open original and anonymised file
	fd_original = open(originalFile, newline='')
	fd_anonymised = open(anonymisedFile, newline='')
	original_reader = csv.reader(fd_original, delimiter=separator)
	anonymised_reader = csv.reader(fd_anonymised, delimiter=separator)

	tabOri = defaultdict(int)
	tabAno = defaultdict(int)
	for lineOri, lineAno in zip(original_reader, anonymised_reader):

		#--- Original file
		key = (round(float(lineOri[2]),size), round(float(lineOri[3]),size))
		tabOri[key] += 1

		#--- Anonymisation file
		if lineAno[0] != "DEL":
			gps2 = (round(float(lineAno[2]),size), round(float(lineAno[3]),size))
			tabAno[gps2] +=1

	nb_cellule = int(len(tabOri)*pt)
	score = 0

	tabOri_sorted = sorted(tabOri.items(), key=lambda t: t[1], reverse=True)
	tabAno_sorted = sorted(tabAno.items(), key=lambda t: t[1], reverse=True)

	finalOri = tabOri_sorted[0:nb_cellule]
	finalAno = dict(tabAno_sorted[0:min(len(tabAno),nb_cellule)])
	
	for cellule in finalOri:
		cellule  = cellule[0]
		if cellule in finalAno:
			score += 1
	
	return score/nb_cellule
