# Nombre de cartes : 49 :
# 3 cartes : plateaux ami, ennemi, vide                                      X
# 2 cartes : only 1 et only 0
# 1 sensibilité : 1 si coup legal qui ne joue pas dans un oeil 0 sinon       X Okf
# 8 libertés : liberté du groupe de la pierre en OHE                         X Okf
# 8 ancienneté de la pierre
# 8 libertés après avoir joué le coup                                        X Okf
# 8 Combien de pierres ennemies seront capturées                             X
# 8 self atari : nombre de pierres amies capturées
# 1 ladder capture
# 1 ladder escape
# 1 current player is black 0 sinon

import numpy as np
import Goban

def print_board_style(l):
    for i in range(0,len(l),9):
        print (' '.join(str(j) for j in l[i:i+9]))

def is_on_corner(fmove):
    return (fmove==0 or fmove==8 or fmove==72 or fmove==80)

def is_on_edge(fmove):
    return (fmove%9==0 or fmove/8<1 or fmove%9==8 or fmove/9>8)

def playing_in_eye(move,board):
    fmove = board.flatten(move)
    k = 0
    while board._neighbors[board._neighborsEntries[fmove]+k] != -1:
        k+=1
    if is_on_corner(fmove):
        return (k==2)
    if is_on_edge(fmove):
        return (k==3)
    return (k==4)

def get_neighbors_index(move,board):
    if (move==0):
        return [1,9]
    if (move==8):
        return [7,17]
    if (move==72):
        return [63,73]
    if (move==81):
        return [71,80]
    if (move%9==0):
        return [move-9,move+1,move+9]
    if (move%9==8):
        return [move-9,move-1,move+9]
    if (move/8<1):
        return [move-1,move+1,move+9]
    if (move/9>8):
        return [move-9,move-1,move+1]
    return [move-9,move-1,move+1,move+9]

def number_liberties(move,board):
    mycolor = board._board[move]
    if mycolor == board._EMPTY:
        return -1
    moves_to_evaluate = []
    moves_to_evaluate.append(move)
    moves_evaluated = []
    liberties=0
    while moves_to_evaluate:
        m = moves_to_evaluate.pop()
        if board._board[m] == mycolor:
            for n in get_neighbors_index(m,board._board):
                if (not n in moves_evaluated) and (n<81):
                    if board._board[n] == mycolor:
                        moves_to_evaluate.append(n)
                    elif board._board[n] == board._EMPTY:
                        liberties+=1
                        moves_evaluated.append(n)
            moves_evaluated.append(m)
#            k=0
#            while board._neighbors[board._neighborsEntries[move] + k] != -1:
#                if not board._neighbors[board._neighborsEntries[move] + k] in moves_evaluated:
#                    moves_to_evaluate.append(board._neighbors[board._neighborsEntries[move] + k])
#                k+=1
#        elif board._board[m] == board._EMPTY:
#            liberties+=1
#        moves_evaluated.append(m)
    return liberties

def build_liberties_array(board):
    liberties = np.zeros((board._BOARDSIZE**2), dtype='int8')
    for m in range(0,81):
            liberties[m] = number_liberties(m,board)
    return liberties
