# AlphaGo Like
Auteurs :  
[Germon Paul](https://github.com/pgermon) and [Martin Hugo](https://github.com/ScarfZapdos).


## Principe de fonctionnement et Objectif
Ce projet a pour but de fournir une implémentation similaire à AlphaGo pour un joueur de Go.  
L'algorithme est basé sur deux principes des IA :
- un réseau convolutionnel qui calcule les chances de gagner selon une configuration donnée ;
- un réseau convolutionnel qui calcule pour chaque coup de la configuration actuelle une probabilité de gagner ;

Ces deux réseaux sont ensuite utilisés dans un algorithme de recherche par Arbre de Monte-Carlo pour choisir le coup à jouer.  
Le joueur implémenté utilise l'interface de jeu Goban.py de [L. Simon](https://www.labri.fr/perso/lsimon/).

## Lancement du projet

Commencez par  **cloner le répertoire**. 
Les réseaux convolutionnels sont déjà entraînés. Vous pouvez essayer de les entraîner avec d'autre paramètres. 

Pour lancer une partie avec le joueur, faites la commande :  
**python3 namedGame.py mctsPlayer *%autrejoueur%***
