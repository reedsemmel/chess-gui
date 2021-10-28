# Copyright (c) 2021 Chris Degawa, Reed Semmel
# SPDX-License-Identifier: GPL-3.0-only

"""
File: chess.py
Author: Chris Degawa
Date: 10/7/2021
Description:
    Houses information and utilities for the basic chess game.
"""

from typing import List

from board import Board
from fen import FEN
from utils import Coordinates, Piece, Player


class ChessState:
    """Tuple of game state"""


    def __init__(self):
        self.available_moves: "List[tuple[Coordinates, Coordinates]]" = []
        self.current_turn: Player = Player.P1
        self.board: Board = Board.new_default_board()
        self.generate_all_legal_moves()


    def generate_all_legal_moves(self):
        """Populates self.available_moves with all the legal moves for current turn"""

        self.available_moves = []

        for file in range(8):
            for rank in range(8):
                coord = Coordinates(file, rank)
                # Don't care about squares that aren't our pieces
                if not self.board[coord].is_on_side(self.current_turn):
                    continue
                for move in self.board.generate_moves(coord, self.current_turn):
                    self.available_moves.append((coord, move))
        self.available_moves = self.board.prune_illegal_moves(self.available_moves,
            self.current_turn)

class Chess:
    """Chess class to hold the internal state of the chess board"""

    def __init__(self):
        """initialize the chess board"""
        self.state = ChessState()
        # Stores all of the moves in a game
        self.__last_moves: "List[FEN]" = []
        self.current_fen: FEN = FEN()

    def __set_board(self, fen: FEN) -> bool:
        """Set the board to an initial state"""
        if False in fen.valid:
            return False
        self.__last_moves.clear()
        self.__add_board(fen)
        return True

    def __add_board(self, fen: FEN):
        """Add a board to the list of boards"""
        if False in fen.valid:
            return False
        self.__last_moves.append(fen)
        self.current_fen = self.__last_moves[-1]
        return True

    def default_board(self) -> bool:
        """Initialize a default board"""
        return self.__set_board(FEN())

    def import_board(self, fen: str) -> bool:
        """Import a board from a fen code"""
        return self.__set_board(FEN(fen))

    def import_boards(self, fens: "List[FEN]") -> bool:
        """Import boards from a fen codes"""
        return not False in [self.__add_board(fen) for fen in fens]

    def export_board(self) -> FEN:
        """Export the board to a fen code"""
        return self.current_fen

    def export_boards(self) -> "List[FEN]":
        """Export all of the boards to a list of fen codes"""
        return self.__last_moves

    def make_move(self, old: Coordinates, new: Coordinates) -> bool:
        """add a move to the list of moves"""
        move = (old, new)
        if not move in self.state.available_moves:
            return False

        # Apply actual move to the state.
        self.state.board[new] = self.state.board[old]
        self.state.board[old] = Piece.NONE

        self.state.current_turn = Player.P1 if self.state.current_turn == Player.P2 else Player.P2
        self.state.generate_all_legal_moves()
        return True

    def check_move(self, old: Coordinates, new: Coordinates) -> bool:
        """check valid moves for a piece"""
        return (old, new) in self.state.available_moves

    def get_valid_moves(self, current: Coordinates) -> "List[Coordinates]":
        """get a list of valid moves for a piece"""
        ret: "List[Coordinates]" = []
        for move in self.state.available_moves:
            if move[0] == current:
                ret.append(move[1])
        return ret

    def is_in_check(self) -> bool:
        """check if the king is in check"""
        return self.state.board.is_in_check(self.state.current_turn)

    def is_in_checkmate(self) -> bool:
        """check if the king is in checkmate"""
        return self.is_in_check() and len(self.state.available_moves) == 0

    def is_in_stalemate(self) -> bool:
        """Check if there is stalemate (king is not in check but there are no available moves)"""
        return (not self.is_in_check()) and len(self.state.available_moves) == 0

    def get_state(self) -> ChessState:
        """Return the current game state"""
        return self.state

    def piece_at(self, coord: Coordinates) -> Piece:
        """Gets the piece at the coordinates for the current state"""
        return self.state.board[coord] if coord.is_valid() else Piece.NONE
