from playerInterface import *
from Goban import Board
import dataset_builder as db
import numpy as np
import random
import math
import copy
import time
from tensorflow.keras.models import load_model

class myPlayer(PlayerInterface):

    def __init__(self):
        self._board = Board()
        self._mycolor = None
        self._model_priors = load_model('model_priors.h5')

    def getPlayerName(self):
        return "Team 38"

    def getPlayerMove(self):
        if self._board.is_game_over():
            return "PASS"
        move = self.select_move(self._board)
        self._board.play_move(move)
        return Board.flat_to_name(move) 

    def playOpponentMove(self, move):
        self._board.play_move(Board.name_to_flat(move)) 

    def newGame(self, color):
        self._mycolor = color
        self._opponent = Board.flip(color)

    def endGame(self, winner):
        if self._mycolor == winner:
            print("I won :D")
        else:
            print("I lost :(")

    def select_move(self, board_org, max_time=7.4, temperature=1.2):
        start_time = time.time()

        # Create the root node with legal_moves of the board
        root = MCTSNode(board_org.weak_legal_moves(), board_org._nextPlayer)

        # add nodes
        while(True):
            board = copy.deepcopy(board_org)
            node = root

            # Select a node and play its move: EXPLORATION
            while (not node.can_add_child()) and (not board.is_game_over()):
                node = self.select_child(node, board, temperature)
                #board.push(node.move)

            # Add a random child to the node selected if possible
            if node.can_add_child() and not board.is_game_over():
                node = node.add_random_child(board)
                #board.push(node.move)


            # Construct a sample to be predicted by CNN_priors
            to_predict = np.empty((0, 15, board._BOARDSIZE, board._BOARDSIZE), dtype = 'int8')
            valid, sample_features_maps = db.build_history_from_moves(node.list_of_moves, board._BOARDSIZE)

            # If the board is not valid, we consider the node as a loss
            if not valid:
                # Backpropagation : update the win ratio of all the previous nodes
                while node is not None:
                    node.update_win_rate(0)
                    node = node.parent
            
            else:
                to_predict = np.append(to_predict, sample_features_maps, axis = 0)
                # Predict the win_rate from the board
                prediction = self._model_priors.predict(to_predict)

                # Backpropagation : update the win ratio of all the previous nodes
                while node is not None:
                    node.update_winrate(prediction)
                    node = node.parent

            # time over
            if (time.time() - start_time >= max_time):
                break
            
        '''
        # DEBUG
        # scored_moves = [win ratio, move, nb rollouts] for each child of the root
        # sorted by win ratio
        scored_moves = [(child.winning_frac(board_org.next_player()), child.move, child.num_rollouts)
                        for child in root.children]
        scored_moves.sort(key=lambda x: x[0], reverse=True)

        for s, m, n in scored_moves[:5]:
            print('%s - %.3f (%d)' % (m, s, n))'''


        # pick best node : EXPLOITATION
        best_move = -1
        best_ratio = -1.0

        for child in root.children:
            child_ratio = child.winrate()

            if child_ratio > best_ratio:
                best_ratio = child_ratio
                best_move = child.move
        print('Select move %s with win pct %.3f' % (best_move, best_ratio))
        return best_move


    def select_child(self, node, board, temperature):

        # upper confidence bound for trees (UCT) metric
        # total_rollouts = node.num_rollouts #???
        total_rollouts = sum(child.num_rollouts for child in node.children)
        log_rollouts = math.log(total_rollouts)

        best_score = -1
        best_child = None

        # loop over each child.
        for child in node.children:

            # calculate the UCT score.
            win_percentage = child.winning_frac(board.next_player())
            exploration_factor = math.sqrt(log_rollouts / child.num_rollouts)
            uct_score = win_percentage + temperature * exploration_factor

            # Check if this is the best score we've seen so far.
            if uct_score > best_score:
                best_score = uct_score
                best_child = child

        board.play_move(best_child.move)
        return best_child



class MCTSNode():

    def __init__(self, unvisited_moves, color, parent=None, move=None):
        self.parent = parent
        self.move = move
        self.color = color
        self.total_win_score = 0
        self.win_counts = {
            Board._BLACK: 0,
            Board._WHITE: 0,
        }
        self.num_rollouts = 0
        self.children = []
        self.unvisited_moves = unvisited_moves
        random.shuffle(self.unvisited_moves)

        if parent is None:
            self.list_of_moves = [move]
        else:
            self.list_of_moves = parent.list_of_moves
            self.list_of_moves.append(move)

    def add_random_child(self, board):
        new_move = self.unvisited_moves.pop()
        while (new_move == -1) and (board.play_move(new_move) == False):
            if not self.can_add_child():
                return self
            new_move = self.unvisited_moves.pop()
        new_node = MCTSNode(board.weak_legal_moves(), board.flip(board._nextPlayer), self, new_move)
        self.children.append(new_node)
        return new_node

    def update_winrate(self, score):
        self.total_win_score += score
        self.num_rollouts += 1

    def can_add_child(self):
        return len(self.unvisited_moves) > 0

    def is_terminal(self, board):
        return board.is_game_over()

    def winrate(self):
        return self.total_win_score / self.num_rollouts
