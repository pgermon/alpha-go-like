# -*- coding: utf-8 -*-

import math
import time
import multiprocessing
import Goban
import os
import json
from random import randint, choice, randrange
from playerInterface import *

class myPlayer(PlayerInterface):

    def __init__(self):
        self._board = Goban.Board()
        self._mycolor = None
        self._opponent = None
        self._turn = 0

        # Temps pour jouer chaque partie
        self._game_timeout = 300 # 5min
        self._game_t0 = time.time() # temps de début de la partie

        # Temps pour jouer chaque coup (temps alloué dans getPlayerMove())
        self._move_timeout = 0
        self._move_t0 = 0
        self._move_max_time = 10 # 10s max par coup

        # Opening
        self._opening_length = 5 # nombre de coups piochés dans la bibliothèque d'openings
        self._opening_index = 0
        self._games_db = []
        # Chargement de la bibliothèque d'openings
        if os.path.exists('games.json'):
            with open('games.json') as json_file:
                data = json.load(json_file)
            for g in data:
                self._games_db.append(g['moves'])

        self._opening = self.getOpening()

    def getPlayerName(self):
        return "AlphaGO"

    # Initialise l'opening càd la liste des premiers coups à jouer
    def getOpening(self):
        # Sélectionne aléatoirement une partie depuis la base de données
        game = self._games_db[randrange(0, len(self._games_db))]

        # Selectionne un joueur aléatoirement
        player = randint(0, 1)

        # Construit les coups de l'opening en en prenant 1 sur 2 parmi les coups de la partie
        opening = [game[k] for k in range(player, len(game), 2)]

        return opening


    # Retourne le prochain coup de l'opening à jouer
    def getOpeningMove(self):

        if self._opening == None:
            return -1 #PASS

        # Recherche le prochain coup valide dans la liste d'opening
        for i in range(self._opening_index, len(self._opening)):

            # Récupère le coup de l'opening à jouer
            move = self._board.name_to_flat(self._opening[i])

            # Vérifie que le coup est bien valide
            if move in self._board.weak_legal_moves():
                if self._board.push(move):
                    self._board.pop()
                    self._opening_index = i + 1
                    return move

                self._board.pop()

        # si aucun coup n'a été trouvé, on choisit aléatoirement un autre opening
        # et on rappelle la fonction getOpeningMove() dessus
        self._opening = self.getOpening()
        self._opening_index = 0
        return self.getOpeningMove()

    def getPlayerMove(self):
        if self._board.is_game_over():
            print("Referee told me to play but the game is over!")
            return 'PASS'

        move = None

        # Début de partie : sélectionne un coup de l'opening
        if self._turn < self._opening_length:
            move = self.getOpeningMove()

        # Après l'opening : calcule le meilleur coup avec IterativeDeepening + MaxMin + AlphaBeta
        else:

            # si on s'approche de la fin de la partie (5min), on réduit le temps alloué aux coups
            if time.time() - self._game_t0 > self._game_timeout - 10:
                self._move_timeout = 0.5

            # sinon, on augmente le temps alloué à chaque coup progressivement :
            else:
                # Coup n°  : temps alloué : temps total
                # 5  -> 14 : 1s    : 10s
                # 15 -> 24 : 2s    : 30s
                # 25 -> 34 : 3s    : 60s
                # 35 -> 44 : 5.5s  : 115s
                # 45 -> 54 : 7s    : 185s
                # 55 -> 64 : 8.5s  : 270s
                # 65 -> 74 : 10.0s : 340s
                # ...      : 10.0s
                # ==> fin de partie (300s) atteinte au bout du 67ème coup
                turn = self._turn - self._opening_length
                self._move_timeout = 1 + turn // 10 * (1 + (turn // 30) / 2)

                # le timeout ne peut pas dépasser le temps max pour 1 coup
                if self._move_timeout > self._move_max_time:
                    self._move_timeout = self._move_max_time

            # On récupère le meilleur coup à jouer
            move = self.iterativeDeepening()

        self._board.push(move)
        self._turn += 1

        # New here: allows to consider internal representations of moves
        print("I am playing ", self._board.move_to_str(move))
        print("My current board :")
        self._board.prettyPrint()
        # move is an internal representation. To communicate with the interface I need to change if to a string
        return Goban.Board.flat_to_name(move)

    def playOpponentMove(self, move):
        print("Opponent played ", move) # New here
        # the board needs an internal represetation to push the move.  Not a string
        self._board.push(Goban.Board.name_to_flat(move))

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Goban.Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won!!!")
        else:
            print("I lost :(!!")


    # Implémente la recherche du meilleur coup par Iterative Deepening
    def iterativeDeepening(self):
        moves = [] # liste des meilleurs coups trouvés : l'indice correspond à
        # la profondeur de recherche -1 qui nous a permis de trouver ce coup
        depth = 1
        self._move_t0 = time.time()

        # tant qu'il reste du temps, on parcours l'arbre a une profondeur plus élevée
        while time.time() - self._move_t0 < 0.90 * self._move_timeout:

            t1 = time.time()

            # On ajoute le meilleur coup trouvé : maxMinCoupAB() renvoie un couple (coup, valeur)
            moves.append(self.maxMinCoupAB(depth))

            #print("Profondeur : ", depth)
            #print("Temps de recherche : ", time.time() - t1, "s")
            #print("Temps total écoulé : ", time.time() - self._move_t0, "s")
            #print("Temps restant : ", self._move_t0 + self._move_timeout - time.time(), "s")
            depth += 1

        # timeout

        coup = None
        max_val = -math.inf

        # On récupère le meilleur coup parmi ceux trouvés
        for move in moves:
            # move = (coup, valeur)
            if move[1] is None:
                return -1

            elif move[1] > max_val:
                coup = move[0]
                max_val = move[1]

        return coup


    '''
    Retourne le meilleur coup à jouer et sa valeur, selon
    une recherche MinMax + AlphaBeta à profondeur depth
    '''
    def maxMinCoupAB(self, depth=3):
        if self._board.is_game_over() or depth == 0:
            return None

        passMove = -1
        coup = None
        v = None
        bestMoves = [] # liste des meilleurs coups trouvés à valeurs égales

        alpha = -math.inf
        beta = math.inf

        # On parcourt tous les coups valables (on vérifie les super_ko en faisant if push ensuite)
        for m in self._board.weak_legal_moves():

            # S'il ne reste plus assez de temps pour jouer, on sort de la boucle for
            if time.time() - self._move_t0 > 0.9 * self._move_timeout:
                break

            # Sinon, on continue l'exploration de l'arbre
            else:
                # On vérifie que le coup ne donne pas un super_ko
                if self._board.push(m):

                    # On déroule l'algo MinMaxAB à la profondeur inférieure
                    ret = self.minMaxAB(alpha, beta, depth - 1)

                    # Si on trouve un meilleur coup que ceux précédemment trouvés, on les supprime
                    # et on ajoute le nouveau coup trouvé
                    if v is None or ret > v:
                        bestMoves.clear()
                        v = ret
                        bestMoves.append(m)

                    # Si on trouve un coup équivalent à ceux précédemment trouvés, on l'ajoute à la liste
                    elif ret == v:
                        bestMoves.append(m)

                self._board.pop()

        # Nombre de cases vides qui peuvent reach uniquement mycolor (cases capturées)
        nb_captured = self._board._count_areas()[self._mycolor - 1]
        moves = []

        # Pour chaque coup trouvé on vérifie qu'il est vraiment valable
        for m in bestMoves:
            if self._board.push(m):

                # On recalcule le nombre de cases vides capturées après avoir joué le coup
                new_captured = self._board._count_areas()[self._mycolor - 1]
                # Le coup n'est valable que si on ne diminue pas notre nombre de cases capturées
                if new_captured >= nb_captured:
                    moves.append(m)

            self._board.pop()

        # Si on ne trouve aucun coup valable, on PASS
        if len(moves) == 0:
            return (passMove, 0)

        # On choisit un coup parmi les meilleurs coups équivalents trouvés
        coup = choice(moves)
        return (coup, v)


    def maxMinAB(self, alpha, beta, depth=3):
        if self._board.is_game_over():
            res = self._board.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0

        # Si on atteint la profondeur max, on retourne l'évaluation heuristique du plateau
        if depth == 0:
            return self.evaluate()


        for m in self._board.weak_legal_moves():

            # S'il ne reste plus assez de temps pour jouer, on sort de la boucle for
            if time.time() - self._move_t0 > 0.9 * self._move_timeout:
                break

            # Sinon, on continue l'exploration de l'arbre
            else:
                if self._board.push(m):
                    ret = self.minMaxAB(alpha, beta, depth - 1)
                    alpha = max(alpha, ret)
                self._board.pop()
                if alpha >= beta:
                    return beta

        return alpha

    def minMaxAB(self, alpha, beta, depth=3):
        if self._board.is_game_over():
            res = self._board.result()
            if res == "1-0":
                return 400
            elif res == "0-1":
                return -400
            else:
                return 0

        # Si on atteint la profondeur max, on retourne l'évaluation heuristique du plateau
        if depth == 0:
            return self.evaluate()

        for m in self._board.weak_legal_moves():

            # S'il ne reste plus assez de temps pour jouer, on sort de la boucle for
            if time.time() - self._move_t0 > 0.9 * self._move_timeout:
                break

            # Sinon, on continue l'exploration de l'arbre
            else:
                if self._board.push(m):
                    ret = self.maxMinAB(alpha, beta, depth - 1)
                    beta = min(beta, ret)
                self._board.pop()
                if alpha >= beta:
                    return alpha

        return beta


    # Heuristique : évalue la force du plateau pour le joueur
    def evaluate(self):
        score = 0
        # Tend à maximiser le nombre de cases vides capturées par le joueur
        # et à minimiser celles capturées par son adversaire
        captured = self._board._count_areas()
        score += captured[self._mycolor - 1]*2
        score -= captured[self._opponent -1]*2
        score -= captured[2]

        return score


    '''
    Les fonctions suivantes fonctiennent correctement mais ne sont pas utilisées.
    Elles ont été implémentées pour essayer d'améliorer l'heuristique mais sont en réalité trop coûteuses.
    '''

    # Retourne la liste des voisins de fcoord à partir des structures d'accès rapide de Goban
    def getNeighbors(self, fcoord):
        if fcoord == 80:
            return self._board._neighbors[self._board._neighborsEntries[fcoord]: -1]
        return self._board._neighbors[self._board._neighborsEntries[fcoord]:self._board._neighborsEntries[fcoord + 1] - 1]

    # Fonction récursive : retourne la liste des pions qui font partie de la
    # même chaîne de pions que fcoord
    def getString(self, fcoord, seen=None):
        color = self._board[fcoord] # couleur du pion positionné en fcoord
        string = [fcoord]

        # On récupère la liste des voisins de fcoord
        neighbors = self.getNeighbors(fcoord)

        # A la première itération on initialise la liste des pions déjà vus avec fcoord
        if seen is None:
            seen = [fcoord]
        # On enlève les pions déjà vus de la liste des voisins
        else:
            neighbors = [n for n in neighbors if n not in seen]

        # On parcourt chaque voisin de fcoord
        for n in neighbors:
            # seen évolue avec les appels récursifs donc on revérifie que le voisin n n'a pas déjà été vu
            if n not in seen:
                # On ajoute n dans seen
                seen.append(n)

                # Si le voisin est de la même couleur que fcoord,
                if self._board[n] == color:
                    # On ajoute le reste de la chaîne en appelant récursivement
                    # la fonction getString sur le voisin et on met seen à jour
                    new_string, seen = self.getString(n, seen)
                    string.extend(new_string)

        return string, seen

    # Retourne la liste des pions de couleur color
    def getPawnsColor(self, color):
        return [i for i in range(self._board._BOARDSIZE**2) if self._board[i] == color]

    # Retourne une liste de toutes les chaînes de pions de la couleur color
    def getAllStrings(self, color):
        strings = []
        seen = []

        # On récupère tous les pions de couleur color
        pawns = self.getPawnsColor(color)

        # Pour chaque pion de couleur color,
        for p in pawns:
            # si le pion n'est pas encore dans une chaîne déjà vue, on récupère sa chaîne
            # et on l'ajoute dans la liste des chaînes et dans la liste des pions déjà vus
            if p not in seen:
                string, _ = self.getString(p)
                seen.extend(string)
                strings.append(string)

        return strings

    # Calcule le degré de liberté d'une chaîne de pions
    def computeLiberties(self, string):
        liberties = 0
        for p in string:
            neighbors = self.getNeighbors(p)
            for n in neighbors:
                if self._board[n] == Goban.Board._EMPTY:
                    liberties += 1
        return liberties

    # Calcule le nombre de pions de couleur color qui touchent la chaîne
    # de pions string d'une autre couleur
    def stringReachColor(self, string, color):

        # La couleur de la chaîne de pions et la couleur color à atteindre
        # doivent être différentes
        if self._board[string[0]] == color:
            return -1

        seen = []
        nb_reached = 0
        for p in string:
            neighbors = self.getNeighbors(p)
            for n in neighbors:
                if n not in seen and self._board[n] == color:
                    nb_reached += 1
                    seen.append(n)
        return nb_reached

    # Calcule le nombre de cases vides capturées par la couleur color
    def computeCaptured(self, color):
        if color == 0:
            return -1

        opp_color = Goban.Board.flip(color)
        nb_captured = 0

        # On récupère toutes les chaînes de cases vides
        empty_strings = self.getAllStrings(0)

        # Pour chaque chaîne vide, on calcule combien de pions de la couleur adverse elle peut atteindre
        for string in empty_strings:
            # Si la chaîne ne peut atteindre aucun pion adverse, on augmente le nombre de cases capturées
            if self.stringReachColor(string, opp_color) == 0:
                nb_captured += len(string)

        return nb_captured