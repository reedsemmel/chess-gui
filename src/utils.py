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
from operator import attrgetter
from typing import Any, Dict, List, Union

from PyQt5.QtGui import QPixmap


class Coordinates:
    """file and rank coordinate tuple"""

    def __init__(self, alg_or_file: Union[str, int], rank: int = -1):
        if isinstance(alg_or_file, str) and len(alg_or_file) == 2:
            self.file = ord(alg_or_file[0]) - ord('a')
            self.rank = int(alg_or_file[1]) - 1
        elif isinstance(alg_or_file, int) and isinstance(rank, int):
            self.file = alg_or_file
            self.rank = rank
        else:
            self._file = -1
            self._rank = -1

    file = property(attrgetter('_file'))
    rank = property(attrgetter('_rank'))

    @file.setter
    def file(self, value: int):
        self._file = value

    @rank.setter
    def rank(self, value: int):
        self._rank = value

    def is_valid(self) -> bool:
        """Returns true if the coordinates are valid on a 8x8 board"""
        return self.file in range(8) and self.rank in range(8)

    def __add__(self, other: "Coordinates") -> "Coordinates":
        return Coordinates(self.file + other.file, self.rank + other.rank)

    def __mul__(self, scale: int) -> "Coordinates":
        return  Coordinates(self.file * scale, self.rank * scale)

    def __str__(self) -> str:
        """Returns the coordinates as a string"""
        return f"{chr(ord('a') + self._file)}{self._rank + 1}" if self.is_valid() else "--"

    def __eq__(self, other) -> bool:
        """Comparison function"""
        if isinstance(other, Coordinates):
            return self.file == other.file and self.rank == other.rank
        return False

    def __lt__(self, other) -> bool:
        """Comparison function"""
        if isinstance(other, Coordinates):
            if self.file == other.file:
                return self.rank < other.rank
            return self.file < other.file
        return False

    def __gt__(self, other) -> bool:
        """Comparison function"""
        if isinstance(other, Coordinates):
            if self.file == other.file:
                return self.rank > other.rank
            return self.file > other.file
        return False

    def __repr__(self) -> str:
        """Returns the coordinates as a string"""
        return self.__str__()

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
            player == Player.P1 and (self == Piece.WR or self == Piece.WB or self == Piece.WN or
            self == Piece.WQ or self == Piece.WK or self == Piece.WP)
        ):
            return True
        if (
            player == Player.P2 and (self == Piece.BR or self == Piece.BB or self == Piece.BN or
            self == Piece.BQ or self == Piece.BK or self == Piece.BP)
        ):
            return True
        return False

    def is_opponent(self, player: "Player") -> bool:
        """Returns True if the Piece is an opponent's piece"""
        if player == Player.P1:
            opponent = Player.P2
        else:
            opponent = Player.P1
        return self != Piece.NONE and self.is_on_side(opponent)

    def is_pawn(self) -> bool:
        """Returns True if the piece is a pawn"""
        return self == Piece.BP or self == Piece.WP

    def is_rook(self) -> bool:
        """Returns True if the piece is a rook"""
        return self == Piece.BR or self == Piece.WR

    def is_knight(self) -> bool:
        """Returns True if the piece is a knight"""
        return self == Piece.BN or self == Piece.WN

    def is_bishop(self) -> bool:
        """Returns True if the piece is a bishop"""
        return self == Piece.BB or self == Piece.WB

    def is_queen(self) -> bool:
        """Returns True if the piece is a queen"""
        return self == Piece.BQ or self == Piece.WQ

    def is_king(self) -> bool:
        """Returns True if the piece is a king"""
        return self == Piece.BK or self == Piece.WK

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


    class PlayerIntBidirectionalConversionTestCase(unittest.TestCase):
        """Unit test for the Player class to ensure correct int conversion in both directions."""

        def test_player_1(self) -> None:
            """Tests that Player 1 is converted to the correct int and vice versa."""
            self.assertEqual(int(Player.P1), 0, "Player 1 is not 0")
            self.assertEqual(Player(0), Player.P1, "0 is not Player 1")

        def test_player_2(self) -> None:
            """Tests that Player 2 is converted to the correct int and vice versa."""
            self.assertEqual(int(Player.P2), 1, "Player 2 is not 1")
            self.assertEqual(Player(1), Player.P2, "1 is not Player 2")


    class SettingsInvalidInputsTestCase(unittest.TestCase):
        """Unit test for the Settings class to ensure invalid inputs are processed correctly."""

        def setUp(self) -> None:
            """Setup class instance for testing."""
            self.settings: Settings = Settings()

        def test_initial_values(self) -> None:
            """Tests if initial values are configured correctly."""
            self.assertEqual(self.settings.player_name, "Player 1",
                "Player name is not \"Player 1\"")
            self.assertEqual(self.settings.opponent_name, "Player 2",
                "Opponent name is not \"Player 2\"")
            self.assertEqual(self.settings.primary_color, "#573D11",
                "Primary color is not #573D11")
            self.assertEqual(self.settings.secondary_color, "#DCB167",
                "Secondary color is not #DCB167")

        def test_invalid_name_change(self) -> None:
            """Tests that invalid names are rejected."""
            self.settings.change_name("This! is! invalid!")
            self.assertEqual(self.settings.player_name, "Player 1",
                f"Player name was changed from \"Player 1\" to \"{self.settings.player_name}\"")

        def test_invalid_hexes(self) -> None:
            """Tests that invalid hexes are detected as such."""
            self.assertFalse(self.settings._is_valid_hex("#invali"), # pylint: disable=protected-access
                "Invalid hex #invali accepted")
            self.assertFalse(self.settings._is_valid_hex("#dhexes"), # pylint: disable=protected-access
                "Invalid hex #dhexes accepted")
            self.assertFalse(self.settings._is_valid_hex("#12345!"), # pylint: disable=protected-access
                "Invalid hex #12345! accepted")

        def test_invalid_color_changes(self) -> None:
            """Tests that invalid colors are rejected."""
            self.settings.change_primary_color("#invali")
            self.assertEqual(self.settings.primary_color, "#573D11",
                f"Primary color was changed from #573D11 to {self.settings.primary_color}")

            self.settings.change_secondary_color("#dhexes")
            self.assertEqual(self.settings.secondary_color, "#DCB167",
                f"Secondary color was changed from #DCB167 to {self.settings.secondary_color}")


    class SettingsValidInputsTestCase(unittest.TestCase):
        """Unit test for the Settings class to ensure valid inputs are processed correctly."""

        def setUp(self) -> None:
            """Setup class instance for testing."""
            self.settings: Settings = Settings()

        def test_initial_values(self) -> None:
            """Tests if initial values are configured correctly."""
            self.assertEqual(self.settings.player_name, "Player 1",
                "Player name is not \"Player 1\"")
            self.assertEqual(self.settings.opponent_name, "Player 2",
                "Opponent name is not \"Player 2\"")
            self.assertEqual(self.settings.primary_color, "#573D11",
                "Primary color is not #573D11")
            self.assertEqual(self.settings.secondary_color, "#DCB167",
                "Secondary color is not #DCB167")

        def test_valid_name_change(self) -> None:
            """Tests that valid names are accepted."""
            self.settings.change_name("This is valid 123")
            self.assertEqual(self.settings.player_name, "This is valid 123",
                "Failed to change player name from \"Player 1\" to \"This is valid 123\"")

        def test_valid_hexes(self):
            """Tests that valid hexes are detected as such."""
            self.assertTrue(self.settings._is_valid_hex("#123456"), # pylint: disable=protected-access
                "Valid hex #123456 not accepted")
            self.assertTrue(self.settings._is_valid_hex("#cf3445"), # pylint: disable=protected-access
                "Valid hex #cf3445 not accepted")
            self.assertTrue(self.settings._is_valid_hex("#FFF"), # pylint: disable=protected-access
                "Valid hex #FFF not accepted")

        def test_valid_color_changes(self):
            """Tests that valid colors are accepted."""
            self.settings.change_primary_color("#FFF")
            self.assertEqual(self.settings.primary_color, "#FFF",
                "Failed to change primary color from #573D11 to #FFF")

            self.settings.change_secondary_color("#cf3445")
            self.assertEqual(self.settings.secondary_color, "#cf3445",
                "Failed to change secondary color from #DCB167 to #cf3445")


    class CoordinatesUnitTest(unittest.TestCase):
        """Unit tests for the Coordinates class."""

        def test_is_valid(self):
            """Tests the is_valid function."""
            for file in range(8):
                for rank in range(8):
                    coord = Coordinates(file, rank)
                    self.assertTrue(coord.is_valid(),
                                    f'{coord} should be valid.')
            for file in range(ord('a'), ord('h') + 1):
                for rank in range(8):
                    file_rank = chr(file) + str(rank + 1)
                    coord = Coordinates(file_rank)
                    self.assertTrue(coord.is_valid(),
                                    f'{coord} should be valid.')

        def test_is_not_valid(self):
            """Test the is_valid function, but with false options"""
            for file in (-1, 8):
                for rank in range(8):
                    coord = Coordinates(file, rank)
                    self.assertFalse(coord.is_valid(),
                                     f'{file},{rank} should be invalid.')
            for file_rank in ('a9', 'z10'):
                coord = Coordinates(file_rank)
                self.assertFalse(coord.is_valid(),
                                 f'{file_rank} should be invalid.')


    unittest.main()
