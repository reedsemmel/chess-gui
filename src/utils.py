"""
File: utils.py
Author: Alishan Bhayani
Date: 10/4/2021
Description:
    Holds utility classes/functions used across multiple source files.
"""

from enum import Enum, unique

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
