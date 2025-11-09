from math import *
import numpy as np
import datetime
from geopy import distance
from geopy.distance import geodesic
import geopandas as gpd
import matplotlib.pyplot as plt
from shapely.geometry import LineString
import heapq
from math import radians, sin, cos, sqrt, atan2




espagne_limite_lat=43.75
espagne_limite_long=-9.55

latInitial = 48.202047
longInitial = -2.932644


latBut = 16.265
longBut = -61.551

coeff_heursitique_prio = 0.2
nombreDeSurvivants = 5
nombreDeCandidats = 5
deltaTempsGenetique = datetime.timedelta(seconds=21000)
tempsEntreChaqueEvalutionDesDistanceParcouru = datetime.timedelta (seconds=15000)



            # 0    4     8     12    16    20    24    28 (Vitesse en noeud/Angle en degre )
valeurs =   [[0,    0,    0,    0,    0,    0,    0,    0], #20
             [0, 2.40, 4.32, 4.88, 5.12, 5.12, 5.04, 4.72], #30
             [0, 2.72, 4.72, 5.28, 5.44, 5.52, 5.44, 5.28], #40
             [0, 3.28, 5.28, 5.68, 5.84, 5.92, 6.00, 5.92], #50
             [0, 3.68, 5.52, 6.00, 6.16, 6.32, 6.48, 6.48], #60
             [0, 3.84, 5.68, 6.24, 6.56, 6.72, 6.96, 7.04], #70
             [0, 3.92, 5.76, 6.48, 6.88, 7.20, 7.52, 7.84], #80
             [0, 4.00, 5.92, 6.64, 7.20, 7.76, 8.32, 8.80], #90
             [0, 4.08, 6.00, 6.80, 7.44, 8.32, 9.12, 9.92], #100
             [0, 4.00, 6.00, 6.88, 7.76, 8.72, 9.92, 11.1], ##110
             [0, 3.76, 5.92, 6.96, 8.16, 9.12, 10.8, 12.32],##120
             [0, 3.44, 5.68, 6.88, 8.08, 9.60, 11.52, 13.04],##130
             [0, 3.04, 5.36, 6.56, 8.08, 9.60, 12.24, 13.68],##140
             [0, 2.56, 4.96, 6.16, 7.36, 9.28, 12.32, 14.00],##150
             [0, 2.16, 4.32, 5.76, 6.80, 8.24, 10.80, 13.20],##160
             [0, 1.92, 3.84, 5.36, 6.32, 7.52, 9.60, 12.16],##170
             [0, 1.76, 3.52, 5.04, 6.08, 7.04, 8.72, 10.96]] ##180






class case :
   def __init__ (self, vitesseVent, directionVent): ##vitesseVent et DirectionVent sont des tableux en fonction du temps
       self.vitesseVent = vitesseVent*1.9438 ##Convertit en noeuds
       if vitesseVent >= 28:
           self.vitesseVent = 27.99
       self.directionVent = directionVent
 
   def effetSurBateau(self, orientationDuBateau, duree):
   
       capBateau = (orientationDuBateau - self.directionVent[trouverTemps(duree)]) % 180 
       if capBateau < 20 :
           return 0


       valeurGauche  = int(self.vitesseVent[trouverTemps(duree)] - (self.vitesseVent[trouverTemps(duree)] %4))
       valeurDroite = valeurGauche + 4
       valeurHaut= int(capBateau - capBateau%10)
       valeurBas = int(valeurHaut + 10)
       
       procheHaut = 1 - (capBateau - valeurHaut )/10
       procheBas = 1 - (valeurBas - capBateau)/10
       procheGauche = 1 - (self.vitesseVent[trouverTemps(duree)] - valeurGauche )/4
       procheDroite = 1 - (valeurDroite - self.vitesseVent[trouverTemps(duree)] )/4
     
       valeurHautGauche = valeurs[(valeurHaut-20)//10][valeurGauche//4] * procheHaut* procheGauche
       valeurHautDroit = valeurs[(valeurHaut-20)//10][valeurDroite//4] * procheHaut* procheDroite
       valeurBasGauche = valeurs[(valeurBas-20)//10][valeurGauche//4] * procheBas* procheGauche
       valeurBasDroit = valeurs[(valeurBas-20)//10][valeurDroite//4] * procheBas* procheDroite
       
       return  valeurHautGauche + valeurHautDroit+ valeurBasGauche + valeurBasDroit


cadrillage = np.load('grille.npy', allow_pickle = 'TRUE') ## cadrillage[longitude][lattitude]
longitude = np.load('longitude.npy', allow_pickle = 'TRUE') ## case = cadrillage[a][b][c] pour savoir a quoi ca correspond : longitude[a]
latitude = np.load('latitude.npy', allow_pickle = 'TRUE')
temps = np.load('temps.npy', allow_pickle = 'TRUE')

def calculer_direction(lat1, long1, lat2, long2):
    # Convertir les latitudes et longitudes en radians
    lat1_rad = radians(lat1)
    long1_rad = radians(long1)
    lat2_rad = radians(lat2)
    long2_rad = radians(long2)
    
    # Calculer la différence de longitude
    delta_long = long2_rad - long1_rad
    
    # Direction en radians
    y = sin(delta_long)
    x = cos(lat1_rad) * sin(lat2_rad) - sin(lat1_rad) * cos(lat2_rad) * cos(delta_long)
    cap_rad = atan2(y, x)
    
    if cap_rad < 0:
        cap_rad += 2 *pi
    
    return cap_rad*180/pi

def trouverLat(lat):
    i = 0
    taille = len(latitude)
    while i < taille - 1 and latitude[i] <= lat:
        i += 1
    return i


def trouverLong(long):
    i = 0
    taille = len(longitude)
    while i < taille - 1 and longitude[i] <= long:
        i += 1
    return i



def trouverTemps(duree):
    i = 0
    taille = len(temps)
    while (temps[i] <= duree and i < taille -1 ) :
         i+=1
    return i


def trouverCase(lat,long):
   return cadrillage[trouverLong(long)][trouverLat(lat)]


def evaluationDuTempsEnLigneDroite (lat1, long1, lat2, long2, date) :
    case2 = trouverCase(lat2, long2)
    case1 = trouverCase(lat1, long1)
    distance_totale = distance.distance((lat1, long1), (lat2, long2)).km*1000
    current_lat = lat1
    current_lon = long1
    date_actuelle = date
    vitesse_saturation = 0
    ##cap = atan2((lat2 - lat1), (long2 - long1))
    cap = calculer_direction(lat1 ,long1, lat2, long2)
    distance_parcourue_totale = 0
    while case2 != case1 and distance_parcourue_totale < distance_totale:
        vitesse_actuelle = case1.effetSurBateau(cap, date_actuelle)
        if vitesse_actuelle == 0:
            vitesse_saturation += 1
        if vitesse_actuelle != 0:
            vitesse_saturation = 0
        if vitesse_saturation == 10:
            return temps[len(temps)-1]
        distance_parcourue = vitesse_actuelle * tempsEntreChaqueEvalutionDesDistanceParcouru.total_seconds()
        distance_parcourue_totale += distance_parcourue
        current_lat += (distance_parcourue / distance_totale) * (lat2 - lat1)
        current_lon += (distance_parcourue / distance_totale) * (long2 - long1)
        case1 = trouverCase(current_lat, current_lon)
        date += tempsEntreChaqueEvalutionDesDistanceParcouru
    return (date-date_actuelle)

def EndroitArriveEnLigneDroite(lat, long, direction, dt, date) : 
    temps = datetime.timedelta(seconds=0)
    direction_actuelle = direction*180/np.pi
    latFinal = lat
    longFinal = long
    while temps<dt :
        temps += tempsEntreChaqueEvalutionDesDistanceParcouru
        case = trouverCase(latFinal, longFinal)
        vitesse = case.effetSurBateau(direction, date+temps)
        distance1 = vitesse * tempsEntreChaqueEvalutionDesDistanceParcouru.total_seconds()
        arrive = geodesic(kilometers=(distance1/1000)).destination((latFinal, longFinal), direction_actuelle)
        latFinal = arrive.latitude
        longFinal = arrive.longitude
    return (latFinal, longFinal)
       

def distance2 (coord1, coord2):
    # Rayon moyen de la Terre en kilomètres
    R = 6371.0
            
    lat1 = radians(coord1[0])
    lon1 = radians(coord1[1])
    lat2 = radians(coord2[0])
    lon2 = radians(coord2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1
    
    # Formule de Haversine
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    
    # Distance entre les deux points en kilomètres
    return R*c

def distance_moyenne_coordonnees(coordonnees):
    total_distance = 0
    nb_pairs = 0
            
    for i in range(len(coordonnees)):
        for j in range(i + 1, len(coordonnees)):
            total_distance += distance2 (coordonnees[i], coordonnees[j])
            nb_pairs += 1
                    
    moyenne_distance = total_distance / (nb_pairs + 1)
    return moyenne_distance



def trouverCandidats (nbCandidats, dt, lat1, long1, antecedant, lat2, long2, date) : ##envoie l'enveloppe convexe accesible en dt, avec un précision de nbCandidats
    rep = []
    ##cap = atan2((lat2-lat1),(long2-long1))
    cap = calculer_direction(lat1 ,long1, lat2, long2) 
    for i in range(nbCandidats) :
        direction = (((-1)**i)*i*np.pi/nbCandidats + cap*pi/180)%2*np.pi  ##en radians
        latArriv, longArriv = EndroitArriveEnLigneDroite (lat1, long1, direction*180/np.pi, dt, date)
        if latArriv >= espagne_limite_lat or longArriv <= espagne_limite_long:
            temps = date + (evaluationDuTempsEnLigneDroite(lat1,long1, latArriv, longArriv, date))
            score = evaluationDuTempsEnLigneDroite(latArriv , longArriv , lat2 ,long2 ,date)
            if latArriv != lat1 or longArriv != long1:
                rep +=  [[latArriv, longArriv, (antecedant + [(lat1, long1)]), temps, score, True]]
    return rep


def remplirLeTableau (nbCandidats, dt, lat1, long1, lat2, long2, tabDesCandidats, antecedant, date) :
    t = trouverCandidats (nbCandidats, dt, lat1, long1, antecedant,lat2, long2, date)
    return tabDesCandidats + t

def choisirLesCandidats(tabDesCandidats, nombreDeSurvivants):  
    nbChoisi = 0
    listeDesChoisis = []
    moyenne = distance_moyenne_coordonnees (tabDesCandidats)
    dist_min = 0
    while nbChoisi < nombreDeSurvivants:
        indice = maxvalide(tabDesCandidats, dist_min,listeDesChoisis )
        listeDesChoisis.append(tabDesCandidats[indice].copy()) 
        tabDesCandidats[indice][5] = False
        dist_min += moyenne/ nombreDeSurvivants
        nbChoisi+=1
    return listeDesChoisis

def maxvalide(tab, dist_min, deja_choisi):
    min = tab[0][4]
    rep = 0
    for i in range (len(tab)) :
        dist_ok = True
        for j in range(len(deja_choisi)) : 
            dist_ok = dist_ok and (distance2(tab[i], deja_choisi[j])>= dist_min) 
        if (tab [i][5] and min >= tab[i][4] and dist_ok) :
            min = tab[i][4]
            rep = i
    return rep


ocean = gpd.read_file("data.zip")
ax = ocean.plot()

def algoGenetique(lat1, long1, lat2, long2, nbCandidats, nbSurvivants, dt, date, candidatsActuels = [[latInitial, longInitial, [], 0, 0, True]], compte=0) : ## candidats = list de [lat, long, antécédant(lat, long, date), date, score, booléen]
   if compte==1000:
       return candidatsActuels[0][2]
   tabCandidats = []
   candidatsTemporaire = []
   for i in range (len(candidatsActuels)) :
       ##if  trouverCase(candidatsActuels[i][0], candidatsActuels[i][1]) == trouverCase(lat2, long2):
       if abs(candidatsActuels[i][0] - lat2) < 1 and abs(candidatsActuels[i][1] - long2) < 1:
           return candidatsActuels[i][2]
           
       candidatsTemporaire += trouverCandidats(nbCandidats, dt, candidatsActuels[i][0], candidatsActuels[i][1], candidatsActuels[i][2],lat2, long2, date)
   tabCandidats = choisirLesCandidats(candidatsTemporaire, nbSurvivants)
   return algoGenetique (lat1,long1, lat2, long2, nbCandidats, nbSurvivants, dt, date+dt, tabCandidats, compte+1)




def heursitique_fil_prio1 (lat, long, temps) :
 return ( evaluationDuTempsEnLigneDroite (lat, long, latBut, longBut, temps) + temps*coeff_heursitique_prio )


def heursitique_fil_prio2 (lat, long, temps) :
 return distance2 ([lat, long],  [latBut, longBut]) 


vu = [[False  for i in range (len(longitude))] for j in range(len(latitude))]


def trouverCandidatsFile (nbCandidats, dt, lat1, long1, antecedant, lat2, long2, date) : 
   rep = []
   cap = calculer_direction(lat1 ,long1, lat2, long2)
   temps = date + dt 
   for i in range(nbCandidats) :
       direction = (((-1)**i)*i*np.pi/nbCandidats + cap*pi/180)%2*np.pi  ##en radians
       latArriv, longArriv = EndroitArriveEnLigneDroite (lat1, long1, direction*180/np.pi, dt, date)
       score = heursitique_fil_prio1 ( latArriv, longArriv, temps)
       if not vu[trouverLat(latArriv)][trouverLong (longArriv)] : 
            rep += [[latArriv, longArriv, (antecedant + [(lat1, long1)]), temps, score]]
            vu[trouverLat(latArriv)][trouverLong (longArriv)] = True
   return rep


def A_star (lat2, long2, nbCandidats, dt, file_prio = [ (heursitique_fil_prio1(latInitial, longInitial, datetime.timedelta()), [latInitial, longInitial, [], datetime.timedelta()])], date=datetime.timedelta() ):
 ( _ , ptActuel) = heapq.heappop(file_prio) 
 cand = trouverCandidatsFile (nbCandidats, dt, ptActuel[0], ptActuel[1], ptActuel[2], lat2, long2, ptActuel[3])
 for j in range(len(cand)):
     if trouverCase (cand[j][0], cand[j][1]) == trouverCase (lat2, long2) :
         return date
     heapq.heappush(file_prio, (cand[j][4].total_seconds(), (cand[j])))
 return  A_star (lat2, long2, nbCandidats, dt, file_prio, date+dt)


