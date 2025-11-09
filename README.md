# Routage Météo pour la Route du Rhum (Projet TIPE)

[![Langage Python](https://img.shields.io/badge/Python-3.9-blue.svg)](https://www.python.org/)

Algorithme de routage météo (Algorithme Génétique et A*) en Python pour trouver la trajectoire optimale pour une course transatlantique.

## 📍 Contexte

Ce projet a été réalisé dans le cadre de mon TIPE. L'objectif est de simuler la Route du Rhum et de trouver la trajectoire minimisant le temps de parcours en fonction des données météo (fichiers GRIB) et des performances du bateau (polaires de vitesse).

Le résultat obtenu sur les données de la course 2022 est un temps de **10 jours, 5 heures et 52 minutes**.

##  Fonctionnalités

* Lecture et interpolation des données météo (fichiers GRIB).
* Modélisation de la vitesse du bateau via les polaires de vitesse.
* Implémentation d'un **Algorithme Génétique** pour l'exploration de l'espace des routes.
* Implémentation d'un algorithme **A*** comme base de comparaison.
* **Gestion des obstacles (terres)** par diversification de la sélection des candidats, résolvant le "problème de l'Espagne".

## Installation

Les dépendances de ce projet sont listées dans `requirements.txt`.

```bash
pip install -r requirements.txt
