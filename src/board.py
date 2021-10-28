#!/usr/bin/env python

# Copyright (c) 2021 Reed Semmel, Alishan Bhayani
# SPDX-License-Identifier: GPL-3.0-only

"""
File: board.py
Author: Reed Semmel
Date: 2021-10-21
Description:
    Board class
"""

from copy import deepcopy
from utils import Coordinates, Piece, Player


class Board:
    """A wrapper for an 8x8 list of pieces to use coordinates to index"""

    # Basic 8 directions in chess
    DIRECTION = (
        Coordinates(1, 0),
        Coordinates(0, 1),
        Coordinates(-1, 0),
        Coordinates(0, -1),
        Coordinates(1, 1),
        Coordinates(-1, 1),
        Coordinates(1, -1),
        Coordinates(-1, -1),
    )

    def __init__(self):
        self._grid: "list[list[Piece]]" = [
            [Piece.NONE for _ in range(8)] for _ in range(8)]

    def __getitem__(self, coord: Coordinates):
        # This is a low level primitive, caller should verify that the coords
        # are valid
        assert coord.is_valid
        return self._grid[coord.file][coord.rank]

    def __setitem__(self, coord: Coordinates, piece: Piece):
        assert coord.is_valid
        self._grid[coord.file][coord.rank] = piece

    @classmethod
    def new_empty_board(cls):
        """Creates a new empty board"""
        return cls()

    @staticmethod
    def new_default_board():
        """Creates a new board in the starting position"""
        board = Board()

        black_piece = (Piece.BR, Piece.BN, Piece.BB, Piece.BQ, Piece.BK,
                       Piece.BB, Piece.BN, Piece.BR)
        white_pieces = (Piece.WR, Piece.WN, Piece.WB, Piece.WQ, Piece.WK,
                        Piece.WB, Piece.WN, Piece.WR)

        for file in range(8):
            board[Coordinates(file, 7)] = black_piece[file]
            board[Coordinates(file, 6)] = Piece.BP
            board[Coordinates(file, 1)] = Piece.WP
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

    def generate_knight_moves(self, coords: Coordinates, player: Player) -> "list[Coordinates]":
        """Generates all the moves a knight can perform"""
        assert coords.is_valid and self[coords].is_knight(
        ) and self[coords].is_on_side(player)
        # Knights move in an L and can jump over pieces
        knight_directions = (
            Coordinates(1, 2),
            Coordinates(-1, 2),
            Coordinates(1, -2),
            Coordinates(-1, -2),
            Coordinates(2, 1),
            Coordinates(-2, 1),
            Coordinates(2, -1),
            Coordinates(-2, -1),
        )

        valid_moves = []
        for offset in knight_directions:
            new_coords = coords + offset
            # The move is only valid there is a blank or opponent tile on the new location
            if new_coords.is_valid() and not self[new_coords].is_on_side(player):
                valid_moves.append(new_coords)
        return sorted(valid_moves)

    def generate_king_moves(self, coords: Coordinates, player: Player) -> "list[Coordinates]":
        """Generates all the valid moves for a king"""
        assert coords.is_valid() and self[coords].is_king(
        ) and self[coords].is_on_side(player)
        valid_moves = []
        for offset in Board.DIRECTION:
            new_coords = coords + offset
            if new_coords.is_valid() and not self[new_coords].is_on_side(player):
                valid_moves.append(new_coords)
        return sorted(valid_moves)

    def generate_queen_moves(self, coords: Coordinates, player: Player) -> "list[Coordinates]":
        """Generates all the valid moves for a queen"""
        assert coords.is_valid() and self[coords].is_queen(
        ) and self[coords].is_on_side(player)
        valid_moves = []

        for direction in Board.DIRECTION:
            for scale in range(1, 8):
                new_coords = direction * scale + coords
                if not new_coords.is_valid():
                    break
                if self[new_coords].is_on_side(player):
                    break
                valid_moves.append(new_coords)
                if self[new_coords].is_opponent(player):
                    break
        return sorted(valid_moves)

    def generate_rook_moves(self, coords: Coordinates, player: Player) -> "list[Coordinates]":
        """Generates all the valid moves for a rook"""
        assert coords.is_valid() and self[coords].is_rook(
        ) and self[coords].is_on_side(player)
        valid_moves = []

        for direction in Board.DIRECTION[0:4]:
            for scale in range(1, 8):
                new_coords = direction * scale + coords
                if not new_coords.is_valid():
                    break
                if self[new_coords].is_on_side(player):
                    break
                valid_moves.append(new_coords)
                if self[new_coords].is_opponent(player):
                    break
        return sorted(valid_moves)

    def generate_bishop_moves(self, coords: Coordinates, player: Player) -> "list[Coordinates]":
        """Generates all the valid moves for a bishop"""
        assert coords.is_valid() and self[coords].is_bishop(
        ) and self[coords].is_on_side(player)
        valid_moves = []

        for direction in Board.DIRECTION[4:8]:
            for scale in range(1, 8):
                new_coords = direction * scale + coords
                if not new_coords.is_valid():
                    break
                if self[new_coords].is_on_side(player):
                    break
                valid_moves.append(new_coords)
                if self[new_coords].is_opponent(player):
                    break
        return sorted(valid_moves)

    def generate_pawn_moves(self, coords: Coordinates, player: Player) -> "list[Coordinates]":
        """Generates all the valid moves for a pawn"""
        assert coords.is_valid() and self[coords].is_pawn(
        ) and self[coords].is_on_side(player)
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
        for capture_coords in (Coordinates(1, direction), Coordinates(-1, direction)):
            capture_coords = coords + capture_coords
            if capture_coords.is_valid() and self[capture_coords].is_opponent(player):
                valid_moves.append(capture_coords)

        return sorted(valid_moves)

    def generate_moves(self, coords: Coordinates, player: Player) -> "list[Coordinates]":
        """Wrapper to tie each piece function together"""
        assert coords.is_valid()
        if self[coords].is_pawn():
            return self.generate_pawn_moves(coords, player)
        if self[coords].is_rook():
            return self.generate_rook_moves(coords, player)
        if self[coords].is_knight():
            return self.generate_knight_moves(coords, player)
        if self[coords].is_bishop():
            return self.generate_bishop_moves(coords, player)
        if self[coords].is_queen():
            return self.generate_queen_moves(coords, player)
        return self.generate_king_moves(coords, player) if self[coords].is_king() else []

    def is_in_check(self, player: Player) -> bool:
        """Returns true if the player is in check in the current position"""

        king_pos = self.find_king(player)

        # Knights
        knight_directions = (
            Coordinates(1, 2),
            Coordinates(-1, 2),
            Coordinates(1, -2),
            Coordinates(-1, -2),
            Coordinates(2, 1),
            Coordinates(-2, 1),
            Coordinates(2, -1),
            Coordinates(-2, -1),
        )

        def __check_knights(king_pos: Coordinates, player: Player) -> bool:
            for offset in knight_directions:
                pos = king_pos + offset
                if pos.is_valid() and self[pos].is_opponent(player) and self[pos].is_knight():
                    return True
            return False

        def __check_queens(king_pos: Coordinates, player: Player) -> bool:
            for direction in Board.DIRECTION:
                for scale in range(1, 8):
                    pos = king_pos + direction * scale
                    if not pos.is_valid():
                        break
                    if self[pos] == Piece.NONE:
                        continue
                    if self[pos].is_opponent(player) and self[pos].is_queen():
                        return True
                    break
            return False

        def __check_rooks(king_pos: Coordinates, player: Player) -> bool:
            for direction in Board.DIRECTION[0:4]:
                for scale in range(1, 8):
                    pos = direction * scale + king_pos
                    if not pos.is_valid():
                        break
                    if self[pos] == Piece.NONE:
                        continue
                    if self[pos].is_opponent(player) and self[pos].is_rook():
                        return True
                    break
            return False

        def __check_bishops(king_pos: Coordinates, player: Player) -> bool:
            for direction in Board.DIRECTION[4:8]:
                for scale in range(1, 8):
                    pos = direction * scale + king_pos
                    if not pos.is_valid():
                        break
                    if self[pos] == Piece.NONE:
                        continue
                    if self[pos].is_opponent(player) and self[pos].is_bishop():
                        return True
                    break
            return False

        def __check_pawns(king_pos: Coordinates, player: Player) -> bool:
            for direction in (1, -1):
                pos = king_pos + \
                    Coordinates(direction, 1 if player == Player.P1 else -1)
                if pos.is_valid() and self[pos].is_opponent(player) and self[pos].is_pawn():
                    return True
            return False

        if __check_knights(king_pos, player) or __check_queens(king_pos, player) or \
            __check_rooks(king_pos, player) or __check_bishops(king_pos, player) or \
                __check_pawns(king_pos, player):
            return True

        # The king lives another day
        return False

    def move(self, from_coords: Coordinates, to_coords: Coordinates, player: Player) -> None:
        """Moves a piece from one location to another"""
        assert from_coords.is_valid() and to_coords.is_valid()
        assert self[from_coords].is_on_side(player)
        assert self[to_coords] == Piece.NONE
        assert to_coords in self.generate_moves(from_coords, player)
        self[to_coords] = self[from_coords]
        self[from_coords] = Piece.NONE

    def prune_illegal_moves(self, moves: "list[tuple[Coordinates, Coordinates]]", player: Player):
        """Removes illegal moves from the list, which are moves that put yourself in check"""
        moves_copy = deepcopy(moves)
        for move in moves:
            board_copy = deepcopy(self)
            board_copy[move[1]] = board_copy[move[0]]
            board_copy[move[0]] = Piece.NONE
            if board_copy.is_in_check(player):
                moves_copy.remove(move)
        return sorted(moves_copy)
