"""
File: utils.py
Author: Alishan Bhayani
Date: 10/4/2021
Description:
    Holds utility classes/functions used across multiple source files.
"""

from enum import Enum, unique
from re import fullmatch

from PyQt5.QtGui import QPixmap

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
        piece_img = {
            Piece.NONE: QPixmap("assets/blank.png"),
            Piece.WR: QPixmap("assets/wr.png"),
            Piece.WB: QPixmap("assets/wb.png"),
            Piece.WN: QPixmap("assets/wn.png"),
            Piece.WQ: QPixmap("assets/wq.png"),
            Piece.WK: QPixmap("assets/wk.png"),
            Piece.WP: QPixmap("assets/wp.png"),
            Piece.BR: QPixmap("assets/br.png"),
            Piece.BB: QPixmap("assets/bb.png"),
            Piece.BN: QPixmap("assets/bn.png"),
            Piece.BQ: QPixmap("assets/bq.png"),
            Piece.BK: QPixmap("assets/bk.png"),
            Piece.BP: QPixmap("assets/bp.png"),
        }
        return piece_img[piece]

@unique
class Player(Enum):
    """Identifier for the two players in a game."""
    P1 = 0
    P2 = 1

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