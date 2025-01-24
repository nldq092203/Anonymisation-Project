import csv
import sys
from Utils import separator #Définir votre propre séparateur Ex: '\t', ' '

#################################
#         Global variables      #
# To know:                      #
# dx =1 means that you allow    #
# a maximum of 111.195km        #
# 0.0001 : cellule au mètre     #
# 0.001 : cellule à la rue      #
# 0.01 : cellule au quartier    #
# 0.1 : cellule à la ville      #
# 1 : cellule à la région       #
# 10 : cellule au pays          #
#                               #
#################################
dx = 0.1
# 1.	Score Calculation:
# •	Each row starts with a score of 1.
# •	Penalty: For every hour of difference, the score is reduced based on a predefined penalty scale (hourdec).
# •	No penalties are applied for changes across days (e.g., a GPS position shifted from Tuesday 16:00 to Wednesday 16:00 retains full utility).
# 2.	Final Score:
# •	The total score is calculated as the average score across all rows, normalized by the number of valid rows in the anonymized file.
#################################
#         Function              #
#################################
def calcul_utility(diff):
    score = diff*(-1/dx) + 1
    if(score < 0):
        return 0
    return score

#################################
#         Utiliy Function       #
#################################
def main(fd_anon_file, fd_nona_file, parameters=None):
    if parameters is None:
        parameters = {"dx": 0.1}
    
    # Safely access 'dx' with a fallback value
    global dx
    dx = parameters.get("dx", 0.1)
    #variables
    utility = 0
    line_utility= 0
    filesize = 0

    #open the files:
    fd_nona_file = open(fd_nona_file, "r")
    fd_anon_file = open(fd_anon_file, "r")
    nona_reader = csv.reader(fd_nona_file, delimiter=separator)
    anon_reader = csv.reader(fd_anon_file, delimiter=separator)

    #read the files and calcul
    for lineAno, lineNonAno in zip(nona_reader, anon_reader):
        filesize += 1
        if lineAno[0] != "DEL":
            diff_lat = abs(float(lineNonAno[3])-float(lineAno[3]))
            diff_long = abs(float(lineNonAno[2])-float(lineAno[2]))
            diff = diff_lat + diff_long
            line_utility += calcul_utility(diff)
        else:
            line_utility += 0
    utility = line_utility / filesize
    return utility
