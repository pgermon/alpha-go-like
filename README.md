# AlphaGo Like
Auteurs :  
[Germon Paul](https://github.com/pgermon) and [Martin Hugo](https://github.com/ScarfZapdos).


## Principe de fonctionnement
Ce projet a pour but de fournir une implémentation similaire à AlphaGo pour un joueur de Go.  

L'algorithme est basé sur deux réseaux de neurones :
- un premier réseau de neurones convolutif qui prédit la probabilité de gagner du joueur courant à partir d'un plateau de jeu en cours de partie;
- un deuxième réseau de neurones convolutif qui prédit la probabilité de jouer sur chaque case du plateau de jeu donné.

Ces deux réseaux sont ensuite utilisés dans un algorithme de recherche par Arbre de Monte-Carlo pour choisir le meilleur coup à jouer.  
Le joueur implémenté utilise l'interface de jeu Goban.py de [L. Simon](https://www.labri.fr/perso/lsimon/).

## Lancement du projet

Commencez par **cloner le répertoire** puis tapez la commande `pip install -r requirements.txt`.   

Pour lancer une partie entre notre joueur et un joueur random, tapez la commande :  
`python3 namedGame.py mctsPlayer randomPlayer`  

## Organisation du dépôt

Le dépôt se décompose de la manière suivante :

📦alpha-go-like  
 ┣ 📂go-package : contient touts le code source  
 ┃ ┣ 📂model_priors : contient la sauvegarde du CNN_priors  
 ┃ ┣ 📜build_dataset.ipynb : preprocessing des données brutes  
 ┃ ┣ 📜CNN_priors.ipynb : entraînement du CNN prédisant les priors     
 ┃ ┣ 📜dataset_builder.py : fonctions utilitaires pour le preprocessing  
 ┃ ┣ 📜get-end-by-gnugo.py  
 ┃ ┣ 📜GnuGo.py  
 ┃ ┣ 📜gnugoPlayer.py  
 ┃ ┣ 📜Goban.py  
 ┃ ┣ 📜localGame.py  
 ┃ ┣ 📜mctsPlayer.py : notre joueur basé sur un MCTS  
 ┃ ┣ 📜namedGame.py  
 ┃ ┣ 📜playerInterface.py  
 ┃ ┣ 📜randomPlayer.py  
 ┃ ┣ 📜samples-9x9.json.gz   
 ┃ ┗ 📜visualGame.ipynb  
 ┣ 📜README.md  
 ┗ 📜requirements.txt  

 ## Difficultés rencontrées
 Notre joueur `mctsPlayer`ne fonctionne pas dans la version actuelle du projet.  
 En effet, lorsque que nous essayons de simuler la phase de rollouts de l'arbre de Monte-Carlo via notre réseau *CNN_priors*, nous obtenons des erreurs que nous n'arrivons pas à résoudre pour la prédiction sur une donnée d'entrée. Nous pensons que ces erreurs sont dues au processus de sauvegarde/chargement de notre modèle via *tensorflow/Keras* puisque nous n'avons pas ce problème lorsque que nous faisons des prédictions sur le dataset de test juste après l'entraînement. L'erreur est détaillée dans le fichier `mctsPlayer.py` (l. 76-84).

 De plus, nous avons éprouvé beaucoup de difficultés à utiliser *gnugo* pour construire les *targets* nécessaires à l'entraînement du second réseau de neurones. C'est pourquoi le notebook `dataset_builder.ipynb` ne fonctionne pas. Nous l'avions utilisé ultérieurement pour construire le dataset d'entraînement du premier réseau.  
 Ces difficultés ainsi qu'un manque de temps ne nous ont donc pas permis d'entraîner ce second réseau. 