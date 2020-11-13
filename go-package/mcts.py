# -*- coding: utf-8 -*-

class Node:
    _move = None
    _wins = None
    _total = None
    _color = None
    _parent = None
    _children = None


    def __init__(self, color, parent=None, move=move):
        self._wins = 0
        self._total = 0
        self._color = color
        self._parent = parent
        self._move = move
        self._chilren = []

    def add_child(self, child):
        self._children.append(child)

    def update(self, result):
        self._total += 1
        if result:
            self._wins += 1

    
class MCTS:
    _root = None

    def __init__(self, root):
        self._root = root

    def backpropagation(self, node):


    