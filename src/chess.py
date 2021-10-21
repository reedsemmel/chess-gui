# Copyright (c) 2021 Chris Degawa, Reed Semmel
# SPDX-License-Identifier: GPL-3.0-only

"""
File: chess.py
Author: Chris Degawa
Date: 10/7/2021
Description:
    Houses information and utilities for the basic chess game.
"""

from typing import List, NamedTuple, Optional, Tuple
from fen import FEN
from utils import Coordinates, Piece, Player

class Board:
    """A wrapper for an 8x8 list of pieces to use coordinates to index"""
    def __init__(self):
        self._grid: List[List[Piece]] = [[Piece.NONE for _ in range(8)] for _ in range(8)]

    def __getitem__(self, coord: Coordinates):
        if coord.is_valid:
            return self._grid[coord.file][coord.rank]
        else:
            # This class is a low level primitive. Users of the class should
            # validate that the coords are in bounds.
            raise IndexError

    def new_empty_board():
        return Board()

    def new_default_board():
        b = Board()

        black_pieces = [Piece.BR, Piece.BN, Piece.BB, Piece.BQ, Piece.BK,
            Piece.BB, Piece.BN, Piece.BR]
        black_pawns = [Piece.BP for _ in range(8)]
        white_pawns = [Piece.WP for _ in range(8)]
        white_pieces = [Piece.WR, Piece.WN, Piece.WB, Piece.WQ, Piece.WK,
            Piece.WB, Piece.WN, Piece.WR]

        for file in range(8):
            b[Coordinates(file, 7)] = black_pieces[file]
            b[Coordinates(file, 6)] = black_pawns[file]
            b[Coordinates(file, 1)] = white_pawns[file]
            b[Coordinates(file, 0)] = white_pieces[file]

        return b


class ChessState(NamedTuple):
    """Tuple of game state"""

    in_check: bool = False
    who_is_in_check: Optional[Player] = None
    is_stalemate: bool = False
    current_turn: Player = Player.P1
    board: Board = Board.new_default_board()


class Chess:
    """Chess class to hold the internal state of the chess board"""

    def __init__(self):
        """initialize the chess board"""
        self.state = ChessState()
        # Stores all of the moves in a game
        self.__last_moves: List[FEN] = []
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

    def import_boards(self, fens: List[FEN]) -> bool:
        """Import boards from a fen codes"""
        return not False in [self.__add_board(fen) for fen in fens]

    def export_board(self) -> FEN:
        """Export the board to a fen code"""
        return self.current_fen

    def export_boards(self) -> List[FEN]:
        """Export all of the boards to a list of fen codes"""
        return self.__last_moves

    # TODO: this function
    # Design: take a piece and a coordinate, and check if the piece can move to that coordinate
    #         using the make_move function in the FEN class
    # Return: True if the move is valid, False otherwise
    def make_move(self, old: Coordinates, new: Coordinates) -> bool:
        """add a move to the list of moves"""
        return True

    # TODO: this function
    # Design: take a piece and a coordinate, and check if the piece can move to that coordinate
    #         using the make_move function in the FEN class, but doesn't actually make the move
    # Return: True if the move is valid, False otherwise
    def check_move(self, old: Coordinates, new: Coordinates) -> bool:
        """check valid moves for a piece"""
        return True

    # TODO: this function
    # Design: take a piece and a coordinate and return a list of valid moves it can make, can
    #         get nullified by the king being in check
    def get_valid_moves(self, current: Coordinates) -> List[Coordinates]:
        """get a list of valid moves for a piece"""
        return []

    # TODO: this function
    # Design: check if we have a king in check
    # Return: Tuple consisting of True if any king is in check and
    #         True if white is in check else False
    def is_in_check(self) -> Tuple[bool, bool]:
        """check if the king is in check"""
        return FEN.is_in_check(self.current_fen)

    # TODO: this function
    # Design: check if we have a king in checkmate
    # Return: Tuple consisting of True if any king is in checkmate with no valid moves
    #         and True if white is in check else False
    def is_in_checkmate(self) -> Tuple[bool, bool]:
        """check if the king is in checkmate"""
        return FEN.is_in_checkmate(self.current_fen)

    def get_state(self) -> ChessState:
        """Return the current game state"""
        return self.state

    def piece_at(self, coord: Coordinates):
        if coord.is_valid:
            return self.state.board[coord]
        else:
            return Piece.NONE