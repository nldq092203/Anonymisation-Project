import csv
import json
import datetime
separator='\t' #Définir votre propre séparateur Ex: '\t', ' '

from collections import defaultdict
def timedelta_def(): return datetime.timedelta()
def returnnone(): return None
def defaultdicttimedalta(): return defaultdict(timedelta_def)
def defaultdictseption(): return defaultdict(defaultdicttimedalta)
maxdict = lambda dict: max(dict, key=lambda key: dict[key])

#/\/\/\/\/\/\ Nom de la métrique: Extraction des Points d’Intérêts /\/\/\/\/\/\
#Le but de cette métrique est de détecter les points d'intérêts d'un individu. 
#Les points d'intérêts correspondent aux lieux où l'utilisateur a le plus séjourné.
#
#Dans le cadre de ce fichier d'utilité, nous regardons par défaut 3 POI les plus importants pour les 12 semaines du dataset.
#1 POI correspond à trois éléments: Lieu d'habitation (22h à 6h), lieu de travail (9h à 16h) et lieu d'activité (le weekend de 10h à 18h) 
#
#L'idée globale de cette utilité est de s'assurer que l'on retrouve bien dans le fichier anonymisé les lieux clé de la vie d'un individu.
#
#Le score est calculé de la manière suivante :
#	Somme [pour chaque i individu] : 
#		Somme [pour chaque POI] :
#			Si temps_POI_oriFile > temps_POI_anonymFile :
#				temps_POI_anonymFile / temps_POI_oriFile
#			Sinon :
#				temps_POI_oriFile / temps_POI_anonymFile
#Le score est finalement converti sur 1
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

#######################################
# --- Taille des points d'intérêts ---#
#######################################
size = 2
# 4 : cellule au mètre
# 3 : cellule à la rue
# 2 : cellule au quartier
# 1 : cellule à la ville
# 0 : cellule à la région
# -1 : cellule au pays

######################################
# --- Nb de POI à vérifier par ID ---#
######################################
nbPOI = 3
# 3: Vérification des 3 POI les plus fréquentés en terme de temps de présence.

################################
# --- Définition des heures ---#
################################
# Détection des POI -nuit, travail et weekend- durant les heures suivantes:
night_start, night_end = 22, 6
# De 22h00 à 6h00
work_start, work_end = 9, 16
# Add lunch time
lunch_time = [12,13]
# De 9h00 à 16h00
weekend_start, weekend_end = 10, 18

def getMaxElement(theDict):
	result = defaultdict(timedelta_def)
	for _ in range(nbPOI):
		if len(theDict)==0:
			break
		key = maxdict(theDict)
		result[key] = theDict[key]
		del theDict[key]
	return result

last_date_original_tab = defaultdict(returnnone)
last_date_anonymised_tab = defaultdict(returnnone)
def diff_time(key, time1, last_date_tab):
    if last_date_tab[key] is None:
        last_date_tab[key] = time1
        return datetime.timedelta()
    else:
        difference = time1 - last_date_tab[key]
        last_date_tab[key] = time1
        return difference
    

def main(originalFile, anonymisedFile, parameters=None):
	if parameters is None:
		parameters={"size":2,"nbPOI":1,"night_start":22,"night_end":6,"work_start":9,"work_end":16,"weekend_start":10,"weekend_end":18}
	global size
	size = parameters.get("size", 2)
	global nbPOI
	nbPOI = parameters.get("nbPOI", 1)
	global night_start
	night_start = parameters.get("night_start", 22)
	global night_end
	night_end = parameters.get("night_end", 6)
	global work_start
	work_start = parameters.get("work_start", 9)
	global work_end
	work_end = parameters.get("work_end", 16)
	global weekend_start
	weekend_start = parameters.get("weekend_start", 10)
	global weekend_end
	weekend_end = parameters.get("weekend_end", 18)
	
	fd_original = open(originalFile, newline='')
	fd_anonymised = open(anonymisedFile, newline='')
	original_reader = csv.reader(fd_original, delimiter=separator)
	anonymised_reader = csv.reader(fd_anonymised, delimiter=separator)
	
	tabOri = defaultdict(defaultdictseption)
	tabAno = defaultdict(defaultdictseption)

	for lineOri, lineAno in zip(original_reader, anonymised_reader):
	
		#--- Original file
		id = lineOri[0]
		date_time = datetime.datetime.fromisoformat(lineOri[1][:19])
		calendar = date_time.date().isocalendar()
		key = (id)
		#key = (id, calendar[0], calendar[1])
		
		gps = (round(float(lineOri[2]),size), round(float(lineOri[3]),size))
		if date_time.weekday()<5:
			if date_time.time()>datetime.time(night_start,00) or date_time.time()<datetime.time(night_end,00):
				tabOri[key]['night'][gps] += diff_time(key, date_time, last_date_original_tab)
			elif date_time.time()>datetime.time(work_start,00) and date_time.time()<datetime.time(work_end,00) and date_time.time().hour not in lunch_time :
				tabOri[key]['work'][gps] += diff_time(key, date_time, last_date_original_tab)
		# else:
		# 	if date_time.time()>datetime.time(weekend_start,00) and date_time.time()<datetime.time(weekend_end,00):
		# 		tabOri[key]['weekend'][gps] += diff_time(key, date_time, last_date_original_tab)
					
		#--- Anonymisation file
		if lineAno[0] != "DEL":
			date_time = datetime.datetime.fromisoformat(lineAno[1][:19])
			# print(f"Processed Anonymized DateTime: {date_time}")

			gps = (round(float(lineAno[2]),size), round(float(lineAno[3]),size))
			if date_time.weekday()<5:
				# print(f"{date_time.time()}")
				if date_time.time()>datetime.time(night_start,00) or date_time.time()<datetime.time(night_end,00):
					tabAno[key]['night'][gps] += diff_time(key, date_time, last_date_anonymised_tab)
					print(f"diff time in night: {tabAno[key]['night'][gps]}")
				elif date_time.time()>datetime.time(work_start,00) and date_time.time()<datetime.time(work_end,00):
					tabAno[key]['work'][gps] += diff_time(key, date_time, last_date_anonymised_tab)
					print(f"diff time in work: {tabAno[key]['work'][gps]}")
			# else:
			# 	if date_time.time()>datetime.time(weekend_start,00) and date_time.time()<datetime.time(weekend_end,00):
			# 		tabAno[key]['weekend'][gps] += diff_time(key, date_time, last_date_anonymised_tab)

	final_tab_original = defaultdict(defaultdictseption)
	
	final_tab_anonymised = defaultdict(defaultdictseption)
	
	for id in tabOri:
		print (f"Tab {tabOri[id]}")
		print(tabAno[id])
		for type in tabOri[id]:
			final_tab_original[id][type] = getMaxElement(tabOri[id][type])
			print(final_tab_original[id])
			final_tab_anonymised[id][type] = getMaxElement(tabAno[id][type])
			print(final_tab_anonymised[id])
	
	total_size = sum((len(final_tab_original[id][type]) for id in final_tab_original for type in final_tab_original[id]))
	score = 0

	for id in final_tab_original:
		for poi_type in final_tab_original[id]:
			for gps in final_tab_original[id][poi_type]:
				time_second_original = final_tab_original[id][poi_type][gps].total_seconds() if final_tab_original[id][poi_type][gps].total_seconds() > 0 else 0
				time_second_anonymised = final_tab_anonymised[id][poi_type][gps].total_seconds() if final_tab_anonymised[id][poi_type][gps].total_seconds() > 0 else 0
				# print (final_tab_anonymised[id][poi_type])

				# Print for debugging
				print(f"ID: {id}, POI Type: {poi_type}, GPS: {gps}")
				print(f"Original Time: {time_second_original} seconds, Anonymized Time: {time_second_anonymised} seconds")

				if time_second_original == 0 and time_second_anonymised == 0:
					continue
				if time_second_original > time_second_anonymised:
					score += time_second_anonymised / time_second_original
				else:
					score += time_second_original / time_second_anonymised

	
	return score/total_size


result = main ("/Users/quynhnguyen/Documents/Documents/Project Data/Anonymisation Project/Anonymisation-Project/geo_data_generator/origin_data/survey_results_2.csv", "/Users/quynhnguyen/Documents/Documents/Project Data/Anonymisation Project/Anonymisation-Project/anonymisation/ano_data/ano_2.csv")
print (result)