import Goban

# Retourne la liste des voisins de fcoord à partir des structures d'accès rapide de Goban
def getNeighbors(board, fcoord):
    if fcoord == 80:
        return board._neighbors[board._neighborsEntries[fcoord]: -1]
    return board._neighbors[board._neighborsEntries[fcoord]:board._neighborsEntries[fcoord + 1] - 1]

# Fonction récursive : retourne la liste des pions qui font partie de la
# même chaîne de pions que fcoord
def getString(board, fcoord, seen=None):
    color = board[fcoord] # couleur du pion positionné en fcoord
    string = [fcoord]

    # On récupère la liste des voisins de fcoord
    neighbors = getNeighbors(board, fcoord)

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
            if board[n] == color:
                # On ajoute le reste de la chaîne en appelant récursivement
                # la fonction getString sur le voisin et on met seen à jour
                new_string, seen = getString(n, seen)
                string.extend(new_string)

    return string, seen

# Retourne la liste des pions de couleur color
def getPawnsColor(board, color):
    return [i for i in range(board._BOARDSIZE**2) if board[i] == color]

# Retourne une liste de toutes les chaînes de pions de la couleur color
def getAllStrings(color):
    strings = []
    seen = []

    # On récupère tous les pions de couleur color
    pawns = getPawnsColor(color)

    # Pour chaque pion de couleur color,
    for p in pawns:
        # si le pion n'est pas encore dans une chaîne déjà vue, on récupère sa chaîne
        # et on l'ajoute dans la liste des chaînes et dans la liste des pions déjà vus
        if p not in seen:
            string, _ = getString(p)
            seen.extend(string)
            strings.append(string)

    return strings

# Calcule le degré de liberté d'une chaîne de pions
def computeLiberties(board, string):
    liberties = 0
    for p in string:
        neighbors = getNeighbors(board, p)
        for n in neighbors:
            if board[n] == Goban.Board._EMPTY:
                liberties += 1
    return liberties

# Calcule le nombre de pions de couleur color qui touchent la chaîne
# de pions string d'une autre couleur
def stringReachColor(board, string, color):

    # La couleur de la chaîne de pions et la couleur color à atteindre
    # doivent être différentes
    if board[string[0]] == color:
        return -1

    seen = []
    nb_reached = 0
    for p in string:
        neighbors = getNeighbors(board, p)
        for n in neighbors:
            if n not in seen and board[n] == color:
                nb_reached += 1
                seen.append(n)
    return nb_reached

# Calcule le nombre de cases vides capturées par la couleur color
def computeCaptured(color):
    if color == 0:
        return -1

    opp_color = Goban.Board.flip(color)
    nb_captured = 0

    # On récupère toutes les chaînes de cases vides
    empty_strings = getAllStrings(0)

    # Pour chaque chaîne vide, on calcule combien de pions de la couleur adverse elle peut atteindre
    for string in empty_strings:
        # Si la chaîne ne peut atteindre aucun pion adverse, on augmente le nombre de cases capturées
        if stringReachColor(string, opp_color) == 0:
            nb_captured += len(string)

    return nb_captured