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

    # Basic 8 directions in chess
    directions = [
        Coordinates(1, 0),
        Coordinates(0, 1),
        Coordinates(-1, 0),
        Coordinates(0, -1),
        Coordinates(1, 1),
        Coordinates(-1, 1),
        Coordinates(1, -1),
        Coordinates(-1, -1),
    ]


    def __init__(self):
        self._grid: List[List[Piece]] = [[Piece.NONE for _ in range(8)] for _ in range(8)]

    def __getitem__(self, coord: Coordinates):
        # This is a low level primitive, caller should verify that the coords
        # are valid
        assert coord.is_valid
        return self._grid[coord.file][coord.rank]

    def __setitem__(self, coord: Coordinates, piece: Piece):
        assert coord.is_valid
        self._grid[coord.file][coord.rank] = piece

    @staticmethod
    def new_empty_board():
        """Creates a new empty board"""
        return Board()

    @staticmethod
    def new_default_board():
        """Creates a new board in the starting position"""
        board = Board()

        black_pieces = [Piece.BR, Piece.BN, Piece.BB, Piece.BQ, Piece.BK,
            Piece.BB, Piece.BN, Piece.BR]
        black_pawns = [Piece.BP for _ in range(8)]
        white_pawns = [Piece.WP for _ in range(8)]
        white_pieces = [Piece.WR, Piece.WN, Piece.WB, Piece.WQ, Piece.WK,
            Piece.WB, Piece.WN, Piece.WR]

        for file in range(8):
            board[Coordinates(file, 7)] = black_pieces[file]
            board[Coordinates(file, 6)] = black_pawns[file]
            board[Coordinates(file, 1)] = white_pawns[file]
            board[Coordinates(file, 0)] = white_pieces[file]

        return board

    def find_king(self, player: Player) -> Coordinates:
        """Returns the coordinates of the players king"""
        king_piece = Piece.WK if player == Player.P1 else Piece.BK
        for file in range(8):
            for rank in range(8):
                coord = Coordinates(file, rank)
                if self[coord] == king_piece:
                    return coord

        # If we get here this means there isn't a king on the board, which
        # shouldn't be possible.
        assert False

    def generate_knight_moves(self, coords: Coordinates, player: Player) -> List[Coordinates]:
        """Generates all the moves a knight can perform"""
        assert coords.is_valid and self[coords].is_knight() and self[coords].is_on_side(player)
        # Knights move in an L and can jump over pieces
        knight_directions = [
            Coordinates(1, 2),
            Coordinates(-1, 2),
            Coordinates(1, -2),
            Coordinates(-1, -2),
            Coordinates(2, 1),
            Coordinates(-2, 1),
            Coordinates(2, -1),
            Coordinates(-2, -1),
        ]

        valid_moves = []
        for offset in knight_directions:
            new_coords = coords + offset
            # The move is only valid there is a blank or opponent tile on the new location
            if new_coords.is_valid() and not self[new_coords].is_on_side(player):
                valid_moves.append(new_coords)
        return valid_moves

    def generate_king_moves(self, coords: Coordinates, player: Player) -> List[Coordinates]:
        """Generates all the valid moves for a king"""
        assert coords.is_valid() and self[coords].is_king() and self[coords].is_on_side(player)
        valid_moves = []
        for offset in self.directions:
            new_coords = coords + offset
            if new_coords.is_valid() and not self[new_coords].is_on_side():
                valid_moves.append(new_coords)
        return valid_moves

    def generate_queen_moves(self, coords: Coordinates, player: Player) -> List[Coordinates]:
        """Generates all the valid moves for a queen"""
        assert coords.is_valid() and self[coords].is_queen() and self[coords].is_on_side(player)
        valid_moves = []

        for direction in self.directions:
            for scale in range(1, 8):
                new_coords = direction * scale + coords
                if not new_coords.is_valid():
                    break
                if self[new_coords].is_on_side(player):
                    break
                valid_moves.append(new_coords)
                if self[new_coords].is_opponent(player):
                    break
        return valid_moves

    def generate_rook_moves(self, coords: Coordinates, player: Player) -> List[Coordinates]:
        """Generates all the valid moves for a rook"""
        assert coords.is_valid() and self[coords].is_rook() and self[coords].is_on_side(player)
        valid_moves = []

        for direction in self.directions[0:4]:
            for scale in range(1, 8):
                new_coords = direction * scale + coords
                if not new_coords.is_valid():
                    break
                if self[new_coords].is_on_side(player):
                    break
                valid_moves.append(new_coords)
                if self[new_coords].is_opponent(player):
                    break
        return valid_moves

    def generate_bishop_moves(self, coords: Coordinates, player: Player) -> List[Coordinates]:
        """Generates all the valid moves for a bishop"""
        assert coords.is_valid() and self[coords].is_bishop() and self[coords].is_on_side(player)
        valid_moves = []

        for direction in self.directions[4:8]:
            for scale in range(1, 8):
                new_coords = direction * scale + coords
                if not new_coords.is_valid():
                    break
                if self[new_coords].is_on_side(player):
                    break
                valid_moves.append(new_coords)
                if self[new_coords].is_opponent(player):
                    break
        return valid_moves

    def generate_pawn_moves(self, coords: Coordinates, player: Player) -> List[Coordinates]:
        """Generates all the valid moves for a pawn"""
        assert coords.is_valid() and self[coords].is_pawn() and self[coords].is_on_side(player)
        valid_moves = []
        direction = 1 if player == Player.P1 else -1

        # Basic advance. Can only advance if the tile is empty
        new_coord = coords + Coordinates(0, direction)
        if new_coord.is_valid() and self[new_coord] == Piece.NONE:
            valid_moves.append(new_coord)

            # Double advance (only available if we can single advance)
            if player == Player.P1 and coords.rank == 1:
                new_coord = coords + Coordinates(0, direction * 2)
                if new_coord.is_valid() and self[new_coord] == Piece.NONE:
                    valid_moves.append(new_coord)
            if player == Player.P2 and coords.rank == 6:
                new_coord = coords + Coordinates(0, direction * 2)
                if new_coord.is_valid() and self[new_coord] == Piece.NONE:
                    valid_moves.append(new_coord)

        # Capture Diagonally
        for capture_coords in [Coordinates(1, direction), Coordinates(-1, direction)]:
            capture_coords = coords + capture_coords
            if capture_coords.is_valid() and self[capture_coords].is_opponent(player):
                valid_moves.append(capture_coords)

        return valid_moves



    def is_in_check(self, player: Player) -> bool:
        """Returns true if the player is in check in the current position"""

        king_pos = self.find_king(player)

        # Knights
        knight_directions = [
            Coordinates(1, 2),
            Coordinates(-1, 2),
            Coordinates(1, -2),
            Coordinates(-1, -2),
            Coordinates(2, 1),
            Coordinates(-2, 1),
            Coordinates(2, -1),
            Coordinates(-2, -1),
        ]
        for offset in knight_directions:
            pos = king_pos + offset
            if pos.is_valid and self[pos].is_opponent(player) and self[pos].is_knight():
                return True

        # Queens
        for direction in self.directions:
            for scale in range(8):
                pos = direction * scale + king_pos
                if not pos.is_valid():
                    break
                if self[pos] == Piece.NONE:
                    continue
                if self[pos].is_opponent(player) and self[pos].is_queen():
                    return True
                break

        # Rooks
        for direction in self.directions[0:4]:
            for scale in range(8):
                pos = direction * scale + king_pos
                if not pos.is_valid():
                    break
                if self[pos] == Piece.NONE:
                    continue
                if self[pos].is_opponent(player) and self[pos].is_rook():
                    return True
                break

        # Bishops
        for direction in self.directions[4:8]:
            for scale in range(8):
                pos = direction * scale + king_pos
                if not pos.is_valid():
                    break
                if self[pos] == Piece.NONE:
                    continue
                if self[pos].is_opponent(player) and self[pos].is_bishop():
                    return True
                break

        # Pawns
        if player == Player.P1:
            pos = king_pos + Coordinates(1, -1)
            if pos.is_valid() and self[pos] == Piece.BP:
                return True
            pos = king_pos + Coordinates(-1, -1)
            if pos.is_valid() and self[pos] == Piece.BP:
                return True
        else:
            pos = king_pos + Coordinates(1, 1)
            if pos.is_valid() and self[pos] == Piece.WP:
                return True
            pos = king_pos + Coordinates(-1, 1)
            if pos.is_valid() and self[pos] == Piece.WP:
                return True

        # The king lives another day
        return False

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

    def piece_at(self, coord: Coordinates) -> Piece:
        """Gets the piece at the coordinates for the current state"""
        if coord.is_valid:
            return self.state.board[coord]
        return Piece.NONE
