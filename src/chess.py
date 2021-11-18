# Copyright (c) 2021 Chris Degawa, Reed Semmel
# SPDX-License-Identifier: GPL-3.0-only

"""
File: chess.py
Author: Chris Degawa
Date: 10/7/2021
Description:
    Houses information and utilities for the basic chess game.
"""

from typing import List, Optional #pylint: disable=unused-import
from stockfish import Stockfish


from board import Board
from fen import FEN
from utils import Coordinates, Piece, Player


class ChessState: # pylint: disable=too-few-public-methods
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

        # Castling
        king_pos = self.board.find_king(self.current_turn)
        for move in self.board.generate_legal_castle_moves(self.current_turn):
            self.available_moves.append((king_pos, move))

class Chess:
    """Chess class to hold the internal state of the chess board"""

    def __init__(self):
        """initialize the chess board"""
        self.state = ChessState()
        # Stores all of the moves in a game
        self.__last_moves: "List[FEN]" = []
        self.current_fen: FEN = FEN()
        self.__move_history: "List[str]" = []

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

    def __coords_to_algebraic(self, old: Coordinates, new: Coordinates, promotion: 'Optional[Piece]') -> str:
        """Converts coordinates to algebraic notation"""
        ret = f"{old}{new}"
        if promotion is not None:
            ret += str(promotion).lower()
        return ret

    def __algebraic_to_move(self, algebraic: str) -> 'tuple[Coordinates, Coordinates, Optional[Piece]]':
        old = Coordinates(algebraic[0:2])
        new = Coordinates(algebraic[2:4])
        promotion = None
        # This is ugly but it gets the job done
        if len(algebraic) == 5:
            if self.state.current_turn == Player.P1:
                if algebraic[4] == 'q':
                    promotion = Piece.WQ
                elif algebraic[4] == 'r':
                    promotion = Piece.WR
                elif algebraic[4] == 'b':
                    promotion = Piece.WB
                else:
                    promotion = Piece.WN
            else:
                if algebraic[4] == 'q':
                    promotion = Piece.BQ
                elif algebraic[4] == 'r':
                    promotion = Piece.BR
                elif algebraic[4] == 'b':
                    promotion = Piece.BB
                else:
                    promotion = Piece.BN
        return (old, new, promotion)

    def add_engine(self, path: str) -> None:
        """Adds the engine to the chess class"""

        if len(path) == 0:
            self.engine = Stockfish()
        else:
            self.engine = Stockfish(path)
        self.engine.set_position([])

    def make_bot_move(self) -> bool:
        """make a bot move"""
        old, new, promotion = self.__algebraic_to_move(self.engine.get_best_move_time(500))
        return self.make_move(old, new, promotion)


    def make_move(self, old: Coordinates, new: Coordinates, promotion_piece: 'Optional[Piece]' = None) -> bool: # pylint: disable=line-too-long
        """add a move to the list of moves"""
        move = (old, new)
        if not move in self.state.available_moves:
            return False

        self.state.board.move(old, new, self.state.current_turn)

        # Also apply the move to the engine.
        if hasattr(self, "engine"):
            self.engine.make_moves_from_current_position([self.__coords_to_algebraic(old, new, promotion_piece)])

        # Apply the pawn promotion if the new coordinate is on the front or back rank and the piece
        # is a pawn
        if new.rank in (0, 7) and self.state.board[new].is_pawn():
            # It is the callers fault if they don't pass a promotion piece
            assert promotion_piece is not None
            self.state.board[new] = promotion_piece

        self.state.current_turn = Player.P1 if self.state.current_turn == Player.P2 else Player.P2
        self.state.generate_all_legal_moves()

        self.__move_history.append((f"{old}{new}"
            f"{'*' if self.is_in_check() else ''}"
            f"{'#' if self.is_in_checkmate() else ''}"
            f"{str(promotion_piece) if promotion_piece is not None else ''}"))

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

    def get_move_history(self) -> "List[str]":
        """get the move history"""
        return self.__move_history

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

    def get_grid(self) -> "List[List[Piece]]":
        """Gets the current state of the board"""
        return self.state.board.get_grid()

    def get_turn(self) -> Player:
        """Gets the current turn"""
        return self.state.current_turn

    def get_king(self) -> Coordinates:
        """Gets the coordinates of the king"""
        return self.state.board.find_king(self.state.current_turn)
