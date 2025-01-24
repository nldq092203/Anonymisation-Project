from datetime import date
import csv
from Utils import separator #Définir votre propre séparateur Ex: '\t', ' '

#/\/\/\/\/\/\ Nom de la métrique: Ecart de la date /\/\/\/\/\/\
#Le but de cette métrique est de calculer l'écart de date pour chaque ligne du fichier anonymisé
#Ainsi, on s’assure de l’authenticité de la date à laquelle la position GPS a été relevée.
#Le score est calculé de la manière suivante :

#	Chaque ligne vaut 1 points
#		1/3 de point est enlevé par jour d'écart
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

# Calculate the utility score based on the date gap between records in 
# the original (non-anonymized) dataset (nona) and the anonymized dataset (anon)
	# 1.	Score Calculation:
	# •	Each row starts with a score of 1.
	# •	Penalty: If there is a difference in days (within the same week) between the original and anonymized records, 1/3 of a point is subtracted for each day of difference.
	# •	Invalid Data: If the weeks don’t match or the dates are invalid, the computation returns an error.
	# 2.	Final Score:
	# •	The final utility score is calculated as the average score across all valid rows.
def main(nona, anon, parameters={}): #Compute the utility in function of the date gap
    total = 0
    filesize = 0
    fd_nona_file = open(nona, "r")
    fd_anon_file = open(anon, "r")
    nona_reader = csv.reader(fd_nona_file, delimiter=separator)
    anon_reader = csv.reader(fd_anon_file, delimiter=separator)
    for row1, row2 in zip(nona_reader, anon_reader):
        score = 1
        filesize += 1
        if row2[0]=="DEL":
            continue
        if len(row2[1]) >= 10 and len(row2[0]):
            year_na, month_na, day_na = row1[1][0:10].split("-")
            year_an, month_an, day_an = row2[1][0:10].split("-")
            try :
                #Uses the ISO calendar to get both week and day number
                dateanon = date(int(year_an), int(month_an), int(day_an)).isocalendar()
                datenona = date(int(year_na), int(month_na), int(day_na)).isocalendar()
            except: return (-1, filesize)
            if dateanon[1] == datenona[1]: # Weeks must be the same
                dayanon = dateanon[2]
                daynona = datenona[2]
                if datenona[2] != dateanon[2]:
                    # Subtract 1/3 of a point per weekday
                    score -= min([abs(dayanon - daynona), abs(max((dayanon, daynona)) - min((dayanon, daynona)) + 7)]) / 3
            else: return (-1, filesize)
        else: return (-1, filesize)
        total += max(0, score) if row2[0] != "DEL" else 0
    return total / filesize