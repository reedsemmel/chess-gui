#!/usr/bin/env python3

# Copyright (c) 2021 Alishan Bhayani, Reed Semmel, Chris Degawa
# SPDX-License-Identifier: GPL-3.0-only

"""
File: utils.py
Author: Alishan Bhayani
Date: 10/4/2021
Description:
    Holds utility classes/functions used across multiple source files.

Board Layout
File a b c d e f g h  Rank
    │r│n│b│q│k│b│n│r│ 7
    │p│p│p│p│p│p│p│p│ 6
    │ │ │ │ │ │ │ │ │ 5
    │ │ │ │ │ │ │ │ │ 4
    │ │ │ │ │ │ │ │ │ 3
    │ │ │ │ │ │ │ │ │ 2
    │P│P│P│P│P│P│P│P│ 1
    │R│N│B│Q│K│B│N│R│ 0
     0 1 2 3 4 5 6 7
"""

from enum import Enum, unique
from re import fullmatch
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from PyQt5.QtGui import QPixmap


class Coordinates(NamedTuple):
    """file and rank coordinate tuple"""

    # self.file = file - ord('a')
    file: int = -1
    rank: int = -1

    def is_valid(self) -> bool:
        """Returns true if the coordinates are valid on a 8x8 board"""
        return self.file in range(8) and self.rank in range(8)


@unique
class Piece(Enum):
    """All possible types of chess pieces."""
    NONE = 0
    WP = 1
    WR = 2
    WN = 3
    WB = 4
    WQ = 5
    WK = 6
    BP = 7
    BR = 8
    BN = 9
    BB = 10
    BQ = 11
    BK = 12

    @staticmethod
    def get_piece_pixmap(piece) -> QPixmap:
        """Returns the corresponding pixmap for the provided piece."""
        base_path: Path = Path(__file__).parent.parent.resolve() / 'assets'
        piece_img = {
            Piece.NONE: QPixmap(str(base_path / 'blank.png')),
            Piece.WR: QPixmap(str(base_path / 'wr.png')),
            Piece.WB: QPixmap(str(base_path / 'wb.png')),
            Piece.WN: QPixmap(str(base_path / 'wn.png')),
            Piece.WQ: QPixmap(str(base_path / 'wq.png')),
            Piece.WK: QPixmap(str(base_path / 'wk.png')),
            Piece.WP: QPixmap(str(base_path / 'wp.png')),
            Piece.BR: QPixmap(str(base_path / 'br.png')),
            Piece.BB: QPixmap(str(base_path / 'bb.png')),
            Piece.BN: QPixmap(str(base_path / 'bn.png')),
            Piece.BQ: QPixmap(str(base_path / 'bq.png')),
            Piece.BK: QPixmap(str(base_path / 'bk.png')),
            Piece.BP: QPixmap(str(base_path / 'bp.png')),
        }
        return piece_img[piece]

    def is_on_side(self, player: "Player") -> bool:
        """Returns True if the Piece is on the side of player"""
        if (
            player == Player.P1 and self == Piece.WR or Piece.WB or Piece.WN or
            Piece.WQ or Piece.WK or Piece.WP
        ):
            return True
        if (
            player == Player.P2 and self == Piece.BR or Piece.BB or Piece.BN or
            Piece.BQ or Piece.BK or Piece.BP
        ):
            return True
        return False

    def is_opponent(self, player: "Player") -> bool:
        """Returns True if the Piece is an opponent's piece"""
        if player == Player.P1:
            opponent = Player.P2
        else:
            opponent = Player.P1
        return self != Piece.NONE and not self.is_on_side(opponent)

    @staticmethod
    def get_valid_rook_moves(current: Coordinates) -> List[Coordinates]:
        """Returns a list of valid rook moves."""
        if not current.is_valid():
            return []
        moves: List[Coordinates] = [Coordinates(file, current.rank)
                                    for file in range(8)]
        moves += [Coordinates(current.file, rank)
                  for rank in range(8)]
        moves.sort()
        return [move for move in moves if move.is_valid() and move != current]

    @staticmethod
    def get_valid_bishop_moves(current: Coordinates) -> List[Coordinates]:
        """Returns a list of valid bishop moves."""
        if not current.is_valid():
            return []
        moves: List[Coordinates] = [Coordinates(file, rank)
                                    for file in range(8)
                                    for rank in range(8)
                                    if abs(file - current.file) == abs(rank - current.rank)]
        moves.sort()
        return [move for move in moves if move.is_valid() and move != current]

    @staticmethod
    def get_valid_knight_moves(current: Coordinates) -> List[Coordinates]:
        """Returns a list of valid knight moves."""
        if not current.is_valid():
            return []
        moves: List[Coordinates] = [Coordinates(current.file + 2, current.rank + 1),
                                    Coordinates(current.file + 2,
                                                current.rank - 1),
                                    Coordinates(current.file - 2,
                                                current.rank + 1),
                                    Coordinates(current.file - 2,
                                                current.rank - 1),
                                    Coordinates(current.file + 1,
                                                current.rank + 2),
                                    Coordinates(current.file + 1,
                                                current.rank - 2),
                                    Coordinates(current.file - 1,
                                                current.rank + 2),
                                    Coordinates(current.file - 1, current.rank - 2)]
        moves.sort()
        return [move for move in moves if move.is_valid()]

    @staticmethod
    def get_valid_queen_moves(current: Coordinates) -> List[Coordinates]:
        """Returns a list of valid queen moves."""
        return sorted(Piece.get_valid_bishop_moves(current) + Piece.get_valid_rook_moves(current))

    @staticmethod
    def get_valid_king_moves(current: Coordinates) -> List[Coordinates]:
        """Returns a list of valid king moves."""
        if not current.is_valid():
            return []
        moves: List[Coordinates] = [Coordinates(current.file + 1, current.rank + 1),
                                    Coordinates(current.file + 1,
                                                current.rank - 1),
                                    Coordinates(current.file - 1,
                                                current.rank + 1),
                                    Coordinates(current.file - 1,
                                                current.rank - 1),
                                    Coordinates(current.file +
                                                1, current.rank),
                                    Coordinates(current.file -
                                                1, current.rank),
                                    Coordinates(
                                        current.file, current.rank + 1),
                                    Coordinates(current.file, current.rank - 1)]
        moves.sort()
        return [move for move in moves if move.is_valid()]

    @staticmethod
    def get_valid_white_pawn_moves(current: Coordinates) -> List[Coordinates]:
        """Returns a list of valid white pawn moves."""
        if not current.is_valid() or current.rank == 0:
            return []
        if current.rank == 1:
            return sorted([Coordinates(current.file, current.rank + 1)] +
                          [Coordinates(current.file, current.rank + 2)])
        return sorted([Coordinates(current.file, current.rank + 1)])

    @staticmethod
    def get_valid_black_pawn_moves(current: Coordinates) -> List[Coordinates]:
        """Returns a list of valid black pawn moves."""
        if not current.is_valid() or current.rank == 7:
            return []
        if current.rank == 6:
            return sorted([Coordinates(current.file, current.rank - 1)] +
                          [Coordinates(current.file, current.rank - 2)])
        return sorted([Coordinates(current.file, current.rank - 1)])

    @staticmethod
    def return_valid_moves(piece, current: Coordinates) -> List[Coordinates]:
        """Returns valid moves for a certain piece at a certain location"""
        valid_moves: Dict[Piece, Any] = {
            Piece.WR: Piece.get_valid_rook_moves,
            Piece.WB: Piece.get_valid_bishop_moves,
            Piece.WN: Piece.get_valid_knight_moves,
            Piece.WQ: Piece.get_valid_queen_moves,
            Piece.WK: Piece.get_valid_king_moves,
            Piece.WP: Piece.get_valid_white_pawn_moves,
            Piece.BR: Piece.get_valid_rook_moves,
            Piece.BB: Piece.get_valid_bishop_moves,
            Piece.BN: Piece.get_valid_knight_moves,
            Piece.BQ: Piece.get_valid_queen_moves,
            Piece.BK: Piece.get_valid_king_moves,
            Piece.BP: Piece.get_valid_black_pawn_moves,
        }
        return valid_moves[piece](current)

    @staticmethod
    def str_to_piece(piece_str: str) -> "Piece":
        """Converts a single char piece to a Piece using the rules of FEN"""
        str_to_piece: "dict[str, Piece]" = {
            ' ': Piece.NONE,
            'P': Piece.WP,
            'R': Piece.WR,
            'N': Piece.WN,
            'B': Piece.WB,
            'Q': Piece.WQ,
            'K': Piece.WK,
            'p': Piece.BP,
            'r': Piece.BR,
            'n': Piece.BN,
            'b': Piece.BB,
            'q': Piece.BQ,
            'k': Piece.BK,
        }
        return str_to_piece[piece_str]

    def __int__(self) -> int:
        return self.value

    def __str__(self) -> str:
        piece_to_str: "dict[Piece, str]" = {
            Piece.NONE: ' ',
            Piece.WP: 'P',
            Piece.WR: 'R',
            Piece.WN: 'N',
            Piece.WB: 'B',
            Piece.WQ: 'Q',
            Piece.WK: 'K',
            Piece.BP: 'p',
            Piece.BR: 'r',
            Piece.BN: 'n',
            Piece.BB: 'b',
            Piece.BQ: 'q',
            Piece.BK: 'k',
        }
        return piece_to_str[self]


@unique
class Player(Enum):
    """Identifier for the two players in a game."""
    P1 = 0
    P2 = 1

    def __int__(self) -> int:
        return self.value


class Settings:
    """Holds all configurable values for the game and provides a method to modify them."""

    def __init__(self) -> None:
        self.player_name: str = "Player 1"
        self.opponent_name: str = "Player 2"

        self.primary_color: str = "#573D11"
        self.secondary_color: str = "#DCB167"

    def change_name(self, new_name: str, check: bool = True) -> None:
        """Changes player name given it contains only alphanumeric characters."""
        if check:
            if bool(fullmatch("([A-Za-z]|[0-9]|[ ])+", new_name)):
                self.player_name: str = new_name
        else:
            self.player_name: str = new_name

    def change_primary_color(self, new_color_hex: str, check: bool = True) -> None:
        """Changes primary color given the new hex is valid."""
        if check:
            if self._is_valid_hex(new_color_hex):
                self.primary_color: str = new_color_hex
        else:
            self.primary_color: str = new_color_hex

    def change_secondary_color(self, new_color_hex: str, check: bool = True) -> None:
        """Changes secondary color given the new hex is valid."""
        if check:
            if self._is_valid_hex(new_color_hex):
                self.secondary_color: str = new_color_hex
        else:
            self.secondary_color: str = new_color_hex

    @staticmethod
    def _is_valid_hex(color_hex: str) -> bool:
        """Checks if the color hex is valid by using a regex."""
        return bool(fullmatch("^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$", color_hex))


if __name__ == "__main__":
    import unittest

    class PieceUnitTest(unittest.TestCase):
        """Unit tests for the Piece class."""

        coords_to_test = [Coordinates(file, rank)
                          for file in range(8) for rank in range(8)]

        def test_get_valid_rook_moves(self):
            """Tests the get_valid_rook_moves function."""
            def x_y(coord: Coordinates):
                return sorted([Coordinates(i, coord.rank)
                               for i in range(8)
                               if i != coord.file] +
                              [Coordinates(coord.file, i)
                               for i in range(8)
                               if i != coord.rank])

            for coord in self.coords_to_test:
                expected = x_y(coord)
                actual = Piece.get_valid_rook_moves(coord)
                self.assertEqual(expected, actual, f'Rook {coord}\n'
                                 f'  Expected -> {expected}\n'
                                 f'  Actual   -> {actual}')

        def test_get_valid_bishop_moves(self):
            """Tests the get_valid_bishop_moves function."""
            def x_y(coord: Coordinates):
                return sorted([Coordinates(i, j)
                               for i in range(8)
                               for j in range(8)
                               if Coordinates(i, j) != coord and
                               abs(i - coord.file) == abs(j - coord.rank)])

            for coord in self.coords_to_test:
                expected = x_y(coord)
                actual = Piece.get_valid_bishop_moves(coord)
                self.assertEqual(expected, actual, f'Bishop {coord}\n'
                                 f'  Expected -> {expected}\n'
                                 f'  Actual   -> {actual}')

        def test_get_valid_knight_moves(self):
            """Tests the get_valid_knight_moves function."""
            def x_y(coord: Coordinates):
                return sorted([Coordinates(i, j)
                               for i in range(8)
                               for j in range(8)
                               if abs(i - coord.file) == 2 and abs(j - coord.rank) == 1 or
                               abs(i - coord.file) == 1 and abs(j - coord.rank) == 2])

            for coord in self.coords_to_test:
                expected = x_y(coord)
                actual = Piece.get_valid_knight_moves(coord)
                self.assertEqual(expected, actual, f'Knight {coord}\n'
                                 f'  Expected -> {expected}\n'
                                 f'  Actual   -> {actual}')

        def test_get_valid_queen_moves(self):
            """Tests the get_valid_queen_moves function."""
            def x_y(coord: Coordinates):
                return sorted(
                    Piece.get_valid_bishop_moves(coord) + Piece.get_valid_rook_moves(coord))

            for coord in self.coords_to_test:
                expected = x_y(coord)
                actual = Piece.get_valid_queen_moves(coord)
                self.assertEqual(expected, actual, f'Queen {coord}\n'
                                 f'  Expected -> {expected}\n'
                                 f'  Actual   -> {actual}')

        def test_get_valid_king_moves(self):
            """Tests the get_valid_king_moves function."""
            def x_y(coord: Coordinates):
                return sorted([Coordinates(i, j) for i in range(
                    coord.file - 1, coord.file + 2) for j in range(coord.rank - 1, coord.rank + 2)])

            for coord in self.coords_to_test:
                expected = [move for move in x_y(coord) if move.is_valid()]
                expected.remove(coord)
                actual = Piece.get_valid_king_moves(coord)
                self.assertEqual(expected, actual, f'King {coord}\n'
                                 f'  Expected -> {expected}\n'
                                 f'  Actual   -> {actual}')

        def test_get_valid_pawn_moves(self):
            """Tests the get_valid_*_pawn_moves function."""
            def x_y(coord: Coordinates, is_white: bool):
                return [] if is_white and coord.rank == 0 or \
                    not is_white and coord.rank == 7 else \
                    sorted([Coordinates(coord.file, coord.rank + 1)] +
                           [Coordinates(coord.file, coord.rank + 2)]) \
                    if is_white and coord.rank == 1 else \
                    sorted([Coordinates(coord.file, coord.rank - 1)] +
                           [Coordinates(coord.file, coord.rank - 2)]) \
                    if not is_white and coord.rank == 6 else \
                    sorted([Coordinates(coord.file, coord.rank + 1)
                            if is_white else
                            Coordinates(coord.file, coord.rank - 1)])
            for coord in self.coords_to_test:
                for is_white in [True, False]:
                    expected = x_y(coord, is_white)
                    actual = Piece.get_valid_white_pawn_moves(coord) \
                        if is_white else Piece.get_valid_black_pawn_moves(coord)
                    self.assertEqual(expected, actual, f'Pawn {coord} {is_white}\n'
                                     f'  Expected -> {expected}\n'
                                     f'  Actual   -> {actual}')
    unittest.main()
