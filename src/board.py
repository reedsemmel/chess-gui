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
import unittest
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
        assert coord.is_valid()
        return self._grid[coord.file][coord.rank]

    def __setitem__(self, coord: Coordinates, piece: Piece):
        assert coord.is_valid()
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

    def get_grid(self) -> "list[list[Piece]]":
        """Returns the grid of pieces"""
        # We want to copy the grid so that the caller can't modify it
        return deepcopy(self._grid)

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
        assert coords.is_valid() and self[coords].is_knight(
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

        def __check_king(king_pos: Coordinates, player: Player) -> bool:
            for direction in Board.DIRECTION:
                pos = king_pos + direction
                if pos.is_valid() and self[pos].is_opponent(player) and self[pos].is_king():
                    return True
            return False

        if __check_knights(king_pos, player) or __check_queens(king_pos, player) or \
            __check_rooks(king_pos, player) or __check_bishops(king_pos, player) or \
                __check_pawns(king_pos, player) or __check_king(king_pos, player):
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


if __name__ == "__main__":
    class TestBoard(unittest.TestCase):
        """Unit tests for the Board class"""

        def test_getitem(self):
            """Tests the __getitem__ function"""
            board = Board().new_default_board()
            self.assertEqual(board[Coordinates("d2")], Piece.WP)
            self.assertEqual(board[Coordinates("e1")], Piece.WK)

        def test_setitem(self):
            """Tests the __setitem__ function"""
            board = Board().new_default_board()
            board[Coordinates("d2")] = Piece.WN
            self.assertEqual(board[Coordinates("d2")], Piece.WN)

        def test_new_empty_board(self):
            """Tests the new_empty_board function"""
            board = Board().new_empty_board()
            self.assertEqual(board[Coordinates("d2")], Piece.NONE)
            self.assertEqual(board[Coordinates("e1")], Piece.NONE)

        def test_new_default_board(self):
            """Tests the new_default_board function"""
            board = Board().new_default_board()
            self.assertEqual(board[Coordinates("d2")], Piece.WP)
            self.assertEqual(board[Coordinates("e1")], Piece.WK)

        def test_find_king(self):
            """Tests the find_king function"""
            board = Board().new_default_board()
            self.assertEqual(board.find_king(Player.P1), "e1")
            self.assertEqual(board.find_king(Player.P2), "e8")

        def test_generate_knight_moves(self):
            """Tests the generate_knight_moves function"""
            board = Board().new_default_board()
            self.assertEqual(board.generate_knight_moves(Coordinates("g1"), Player.P1),
                             ["f3", "h3"])
            self.assertEqual(board.generate_knight_moves(Coordinates("b1"), Player.P1),
                             ["a3", "c3"])
            board.move(Coordinates("g1"), Coordinates("f3"), Player.P1)
            self.assertEqual(board.generate_knight_moves(Coordinates("f3"), Player.P1),
                             ["d4", "e5", "g1", "g5", "h4"])
            board.move(Coordinates("f3"), Coordinates("g5"), Player.P1)
            self.assertEqual(board.generate_knight_moves(Coordinates("g5"), Player.P1),
                             ["e4", "e6", "f3", "f7", "h3", "h7"])

        def test_generate_bishop_moves(self):
            """Tests the generate_bishop_moves function"""
            board = Board().new_default_board()
            self.assertEqual(board.generate_bishop_moves(
                Coordinates("c1"), Player.P1), [])
            self.assertEqual(board.generate_bishop_moves(
                Coordinates("c8"), Player.P2), [])
            board[Coordinates("b2")] = Piece.NONE
            board[Coordinates("d2")] = Piece.NONE
            board[Coordinates("b7")] = Piece.NONE
            board[Coordinates("d7")] = Piece.NONE
            self.assertEqual(board.generate_bishop_moves(Coordinates("c1"), Player.P1),
                             ["a3", "b2", "d2", "e3", "f4", "g5", "h6"])
            self.assertEqual(board.generate_bishop_moves(Coordinates("c8"), Player.P2),
                             ["a6", "b7", "d7", "e6", "f5", "g4", "h3"])
            board.move(Coordinates("c8"), Coordinates("a6"), Player.P2)
            self.assertEqual(board.generate_bishop_moves(Coordinates("a6"), Player.P2),
                             ["b5", "b7", "c4", "c8", "d3", "e2"])

        def test_generate_rook_moves(self):
            """Tests the generate_rook_moves function"""
            board = Board().new_default_board()
            self.assertEqual(board.generate_rook_moves(
                Coordinates("a1"), Player.P1), [])
            board.move(Coordinates("a2"), Coordinates("a4"), Player.P1)
            self.assertEqual(board.generate_rook_moves(Coordinates("a1"), Player.P1),
                             ["a2", "a3"])
            board.move(Coordinates("a1"), Coordinates("a3"), Player.P1)
            self.assertEqual(board.generate_rook_moves(Coordinates("a3"), Player.P1),
                             ["a1", "a2", "b3", "c3", "d3", "e3", "f3", "g3", "h3"])

        def test_generate_queen_moves(self):
            """Tests the generate_queen_moves function"""
            board = Board().new_default_board()
            self.assertEqual(board.generate_queen_moves(
                Coordinates("d1"), Player.P1), [])
            board.move(Coordinates("d2"), Coordinates("d4"), Player.P1)
            self.assertEqual(board.generate_queen_moves(Coordinates("d1"), Player.P1),
                             ["d2", "d3"])
            board.move(Coordinates("d1"), Coordinates("d3"), Player.P1)
            self.assertEqual(board.generate_queen_moves(Coordinates("d3"), Player.P1),
                             ["a3", "a6", "b3", "b5", "c3", "c4", "d1", "d2",
                              "e3", "e4", "f3", "f5", "g3", "g6", "h3", "h7"])

        def test_generate_king_moves(self):
            """Tests the generate_king_moves function"""
            board = Board().new_default_board()
            self.assertEqual(board.generate_king_moves(
                Coordinates("e1"), Player.P1), [])
            self.assertEqual(board.generate_king_moves(
                Coordinates("e8"), Player.P2), [])
            board.move(Coordinates("e2"), Coordinates("e4"), Player.P1)
            self.assertEqual(board.generate_king_moves(Coordinates("e1"), Player.P1),
                             ["e2"])

        def test_generate_pawn_moves(self):
            """Tests the generate_pawn_moves function"""
            board = Board().new_default_board()
            self.assertEqual(board.generate_pawn_moves(
                Coordinates("a2"), Player.P1), ["a3", "a4"])
            self.assertEqual(board.generate_pawn_moves(
                Coordinates("a7"), Player.P2), ["a5", "a6"])
            board.move(Coordinates("a2"), Coordinates("a4"), Player.P1)
            self.assertEqual(board.generate_pawn_moves(Coordinates("a4"), Player.P1),
                             ["a5"])

        def test_generate_moves(self):
            """Tests the generate_moves function"""
            board = Board().new_default_board()
            self.assertEqual(board.generate_moves(Coordinates("a2"), Player.P1),
                             board.generate_pawn_moves(Coordinates("a2"), Player.P1))
            self.assertEqual(board.generate_moves(Coordinates("a7"), Player.P2),
                             board.generate_pawn_moves(Coordinates("a7"), Player.P2))
            self.assertEqual(board.generate_moves(Coordinates("e1"), Player.P1),
                             board.generate_king_moves(Coordinates("e1"), Player.P1))
            self.assertEqual(board.generate_moves(
                Coordinates("c6"), Player.P2), [])

        def test_is_in_check(self):
            """Tests the is_in_check function"""
            board = Board().new_default_board()
            self.assertFalse(board.is_in_check(Player.P1))
            self.assertFalse(board.is_in_check(Player.P2))
            board[Coordinates("e7")] = Piece.NONE
            board[Coordinates("e5")] = Piece.WR
            self.assertTrue(board.is_in_check(Player.P2))
            self.assertFalse(board.is_in_check(Player.P1))

        def test_prune_illegal_moves(self):
            """Tests the prune_illegal_moves function"""
            board = Board().new_default_board()
            board.move(Coordinates("e7"), Coordinates("e6"), Player.P2)
            board[Coordinates("e5")] = Piece.WR
            board[Coordinates("f5")] = Piece.WP

            avail_moves: list[tuple(Coordinates, Coordinates)] = []
            for move in board.generate_moves(Coordinates("e6"), Player.P2):
                avail_moves.append((Coordinates("e6"), move))
            self.assertEqual(board.prune_illegal_moves(
                avail_moves, Player.P2), [])

    unittest.main()
