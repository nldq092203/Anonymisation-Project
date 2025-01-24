import csv
from Utils import separator #Définir votre propre séparateur Ex: '\t', ' '

#/\/\/\/\/\/\ Nom de la métrique: Ecart de l'heure /\/\/\/\/\/\
#Le but de cette métrique est de calculer l'écart d'heure pour chaque ligne du fichier anonymisé
#Ainsi, on s’assure de l’authenticité à la laquelle la position GPS a été relevée.
#Ici, on ne sanctionne pas la modification d'un jour de la semaine. Une position GPS le mardi à 16h déplacé le mercredi à 16h gardera TOUTE son utilité
#Le score est calculé de la manière suivante :

#	Chaque ligne vaut 1 point
#	Une fraction de point est enlevée à chaque heure d'écart selon le tableau hourdec
#/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\

def main(nona, anon, parameters={}): #Compute the utility in function of the date gap
    total = 0
    filesize = 0
    # Set the amount linked to the hour gap
    hourdec = [1, 0.9, 0.8, 0.6, 0.4, 0.2, 0, 0.1, 0.2, 0.3, 0.4, 0.5,
               0.6, 0.5, 0.4, 0.3, 0.2, 0.1, 0, 0.2, 0.4, 0.6, 0.8, 0.9]
    fd_nona_file = open(nona, "r")
    fd_anon_file = open(anon, "r")
    nona_reader = csv.reader(fd_nona_file, delimiter=separator)
    anon_reader = csv.reader(fd_anon_file, delimiter=separator)
    for row1, row2 in zip(nona_reader, anon_reader):
        score = 1
        filesize += 1
        if row2[0]=="DEL":
            continue
        if len(row2[1]) > 13 and len(row2[0]):
            houranon = int(row2[1][11:13])
            hournona = int(row1[1][11:13])
            if 0 <= houranon < 24 and 0 <= hournona < 24:
                if abs(houranon - hournona):  # Subtract 0,1 points per hour (even if days are identical)
                    score -= hourdec[abs(houranon) - int(hournona)]  # Subtract the amount linked to the hour gap
            else: return (-1, filesize)
        else: return (-1, filesize)
        total += max(0, score) if row2[0] != "DEL" else 0
    return total / filesize