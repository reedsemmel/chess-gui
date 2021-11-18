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
  8 │r│n│b│q│k│b│n│r│ 7
  7 │p│p│p│p│p│p│p│p│ 6
  6 │ │ │ │ │ │ │ │ │ 5
  5 │ │ │ │ │ │ │ │ │ 4
  4 │ │ │ │ │ │ │ │ │ 3
  3 │ │ │ │ │ │ │ │ │ 2
  2 │P│P│P│P│P│P│P│P│ 1
  1 │R│N│B│Q│K│B│N│R│ 0
     0 1 2 3 4 5 6 7
"""

from enum import Enum, unique
from re import fullmatch
from pathlib import Path
from operator import attrgetter
from typing import Any, Dict, List, Union
from PyQt5.QtCore import QSize

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
        return Coordinates(self.file * scale, self.rank * scale)

    def __str__(self) -> str:
        """Returns the coordinates as a string"""
        return f"{chr(ord('a') + self._file)}{self._rank + 1}" if self.is_valid() else "--"

    def __eq__(self, other) -> bool:
        """Comparison function"""
        if isinstance(other, Coordinates):
            return self.file == other.file and self.rank == other.rank
        if isinstance(other, str):
            return self.__str__() == other
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
            player == Player.P1 and self in (Piece.WR, Piece.WB, Piece.WN, Piece.WQ,
                Piece.WK, Piece.WP)
        ):
            return True
        if (
            player == Player.P2 and self in (Piece.BR, Piece.BB, Piece.BN, Piece.BQ,
                Piece.BK, Piece.BP)
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
        return self in (Piece.BP, Piece.WP)

    def is_rook(self) -> bool:
        """Returns True if the piece is a rook"""
        return self in (Piece.BR, Piece.WR)

    def is_knight(self) -> bool:
        """Returns True if the piece is a knight"""
        return self in (Piece.BN, Piece.WN)

    def is_bishop(self) -> bool:
        """Returns True if the piece is a bishop"""
        return self in (Piece.BB, Piece.WB)

    def is_queen(self) -> bool:
        """Returns True if the piece is a queen"""
        return self in (Piece.BQ, Piece.WQ)

    def is_king(self) -> bool:
        """Returns True if the piece is a king"""
        return self in (Piece.BK, Piece.WK)

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
        str_to_piece: Dict[str, Piece] = {
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
        piece_to_str: Dict[Piece, str] = {
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

    def __bool__(self):
        return self != Piece.NONE


@unique
class Player(Enum):
    """Identifier for the two players in a game."""
    P1 = 0
    P2 = 1

    def __int__(self) -> int:
        return self.value


class Settings:
    """Holds all configurable values for the game and provides a method to modify them."""

    DEFAULT_FONT_SIZE: int = 12
    DEFAULT_WINDOW_SIZE: QSize = QSize(853, 480)
    _ALPHA_NUM_REGEX: str = "([A-Za-z]|[0-9]|[ ])+"
    _HEX_REGEX: str = "^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$"

    def __init__(self) -> None:
        self.autoflip: bool = False
        self.mode: GameMode = None
        self.stockfish_path: str = ""
        self.stockfish_difficulty: int = 10
        self.configurables: Dict[str, Dict[str, Any]] = {
            "player_name": {
                "form_header": "Player Name: ",
                "handle_func": lambda value, check=True:
                    self._handle_change("player_name", value, check),
                "max_length": 20,
                "regex": self._ALPHA_NUM_REGEX,
                "value": "Player 1"
            },
            "opponent_name": {
                "form_header": "Opponent Name: ",
                "handle_func": lambda value, check=True:
                    self._handle_change("opponent_name", value, check),
                "max_length": 20,
                "regex": self._ALPHA_NUM_REGEX,
                "value": "Player 2"
            },
            "primary_color": {
                "form_header": "Primary Color: ",
                "handle_func": lambda value, check=True:
                    self._handle_change("primary_color", value, check),
                "max_length": 7,
                "regex": self._HEX_REGEX,
                "value": "#573D11"
            },
            "secondary_color": {
                "form_header": "Secondary Color: ",
                "handle_func": lambda value, check=True:
                    self._handle_change("secondary_color", value, check),
                "max_length": 7,
                "regex": self._HEX_REGEX,
                "value": "#DCB167"
            }
        }

    @property
    def player_name(self) -> str:
        """Returns the player name."""
        return self.configurables["player_name"]["value"]

    @property
    def opponent_name(self) -> str:
        """Returns the opponent name."""
        return self.configurables["opponent_name"]["value"]

    @property
    def primary_color(self) -> str:
        """Returns the primary color."""
        return self.configurables["primary_color"]["value"]

    @property
    def secondary_color(self) -> str:
        """Returns the secondary color."""
        return self.configurables["secondary_color"]["value"]

    def _handle_change(self, configurable: str, value: str, check: bool = True) -> None:
        """Handles a change to a configurable value."""
        if not check or bool(fullmatch(self.configurables[configurable]["regex"], value)):
            self.configurables[configurable]["value"] = value

    def toggle_autoflip(self) -> None:
        """Toggles the autoflip setting."""
        self.autoflip = not self.autoflip


class GameMode(Enum):
    """Specifies the game mode"""
    PVP = 0
    PVC = 1
    CVP = 2
    # player vs player, and computer vs player
