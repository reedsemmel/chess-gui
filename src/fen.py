#!/usr/bin/env python3

# Copyright (c) 2021 Chris Degawa
# SPDX-License-Identifier: GPL-3.0-only

"""
File: fen.py
Author: Chris Degawa
Date: 9/27/2021
Description:
    Houses information and utilites for FEN (Forsyth-Edwards Notation) encoding
    for chess.
"""

from typing import Tuple, Union
import unittest
import numpy
from utils import Piece, Coordinates


class FEN:
    """
    Class to hold and interpret a FEN code

    valid: Tuple[bool, bool] first is used to check if the FEN code is valid
                             the second is used to check if the board is valid
                             and can be printed

    The later fields are only valid if valid[0] is True

    rows: tuple[str, ...] the rows of the chess board, can index using [0-7][0-7]
    turns: str the color to go next
    castling: str the castling rights
    en_passant: str the en passant square
    half_and_full_move_clock: Tuple[int, int] the half move and full move clock
    str(FEN): str returns the FEN code

    a board is considered valid if the analysis board button is
    available at https://lichess.org/editor, excluding checks and mates

    """

    @staticmethod
    def __check_syntax(fields: list[str], rows: list[list[Piece]]) -> bool:
        """Basic syntax checks"""

        def __check_row(row: list[Piece]) -> bool:
            """Check a row for validity"""
            return not (len(row) != 8 or False in [c in Piece for c in row])

        if len(fields) != 6 or len(rows) != 8 or False in [__check_row(row) for row in rows]:
            return False

        # Check turns field
        # Check castling field
        # Check en passant field
        # Check half move clock field and full move clock field
        return not (len(fields[1]) != 1 and fields[1].lower() not in "wb" or
                    False in [x in "-kq" for x in fields[2].lower()] or
                    not fields[3].lower()[0] in "-abcdefgh" or
                    len(fields[3]) == 2 and fields[3][1] not in "12345678" or
                    not fields[4].isdigit() or not fields[5].isdigit())

    def __check_board(self, fields: list[str], rows: list[list[Piece]]) -> bool:
        """Chess piece checks"""

        # Each side can only have 1 king
        if fields[0].count("k") != 1 or fields[0].count("K") != 1:
            return False

        # Pawn on row 0 or 7 check
        if any(i in rows[0] + rows[7] for i in [Piece.BP, Piece.WP]):
            return False

        # Opposing kings can't be next to nor diagonal from each other
        index: int = [x for row in rows for x in row].index(Piece.BK)
        if Piece.WK in self[Piece.get_valid_king_moves(Coordinates(int(index / 8), index % 8))]:
            return False
        return True

    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """Initalize and verify a FEN, default fen is the default chess board"""

        self.valid: Tuple[bool, bool] = (False, False)
        self.rows: numpy.ndarray = numpy.zeros((8, 8), dtype=Piece)
        self.turns: str = ""
        self.castling: str = ""
        self.en_passant: str = ""
        self.half_and_full_move_clock: Tuple[int, int] = (0, 0)

        # Fen code as we received it if we need to print an error
        self.__fen: str = fen

        fields: "list[str]" = list(
            filter("".__ne__, fen.strip().split(" ")))

        if len(" ".join(fields)) == 0:
            return

        rows: "list[list[Piece]]" = []
        for row in fields[0].split("/"):
            currrow: list[Piece] = []
            for char in row:
                if char.isdigit():
                    for _ in range(int(char)):
                        currrow.append(Piece.NONE)
                elif char.lower() in "prbnqk":
                    currrow.append(Piece.str_to_piece(char))
            rows.insert(0, currrow)

        if FEN.__check_syntax(fields, rows) is False:
            return

        self.valid: Tuple[bool, bool] = (False, True)
        self.rows: numpy.ndarray = numpy.array(rows)
        self.turns: str = fields[1]
        self.castling: str = fields[2]
        self.en_passant: str = fields[3]
        self.half_and_full_move_clock: Tuple[int, int] = (
            int(fields[4]), int(fields[5]))

        if self.__check_board(fields, rows) is False:
            return

        self.valid: Tuple[bool, bool] = (True, True)

    def get_fen(self) -> str:
        """Get the FEN code"""
        if not self.valid[0]:
            return self.__fen
        board: list[str] = []

        for row in list(reversed(self.rows)):
            currow: str = ""
            count: int = 0
            for piece in row:
                if piece is Piece.NONE:
                    count += 1
                    continue
                if count > 0:
                    currow += str(count)
                    count = 0
                currow += str(piece)
            if count > 0:
                currow += str(count)
            board.append(currow)

        return " ".join([
            "/".join(board),
            self.turns,
            self.castling,
            self.en_passant,
            str(self.half_and_full_move_clock[0]),
            str(self.half_and_full_move_clock[1])
        ])

    def __str__(self) -> str:
        return self.get_fen()

    def __getitem__(self, key: Union[str, int, Coordinates, list[Coordinates]]) -> Piece:
        """
        Returns either the row or piece.
        Can be indexed using 1-8 or a-h or using algebraic notation a8
        """
        if isinstance(key, list):
            return [self.__getitem__(x) for x in key]
        if isinstance(key, Coordinates):
            return self.rows[key.file][key.rank]
        if (isinstance(key, int) or key.isdigit()) and int(key) in range(8):
            return self.rows[int(key)]
        if len(key) == 1 and key[0].lower() in "abcdefg":
            return self.rows[:, ord(key[0].lower()) - ord('a')]
        if len(key) == 2 and key[0].lower() in "abcdefg" and int(key[1]) in range(8):
            return self.__getitem__(key[0])[int(key[1])]
        return ""

    # TODO: this function
    # Design: check if a fen code has a king in check
    # Return: Tuple consisting of True if any king is in check and True if white is in check else False
    @staticmethod
    def is_in_check(fen) -> Tuple[bool, bool]:
        """Check if a the king is in check"""
        return (False, False)

    # TODO: this function
    # Design: check if a fen code has a king in checkmate
    # Return: Tuple consisting of True if any king is in checkmate with no valid moves
    #         and True if white is in check else False
    @staticmethod
    def is_in_checkmate(fen) -> Tuple[bool, bool]:
        """Check if a king is in checkmate"""
        index: int = [x for row in fen.rows for x in row].index(Piece.BK)
        if fen.is_in_check(fen) and fen[Piece.get_valid_king_moves(Coordinates(int(index / 8), index % 8))] == []:
            return (True, False)
        return (False, False)

    def get_valid_moves(self, coordinates: Coordinates) -> list[Coordinates]:
        """Get all valid moves for a piece, """
        piece: Piece = self[coordinates]
        if piece is Piece.NONE or self.is_in_checkmate(self):
            return []
        return Piece.return_valid_moves(piece, coordinates)

    # TODO: add checks for check and mates and stuff
    def make_move(self, old: Coordinates, new: Coordinates) -> bool:
        """Tries to make a move if valid and returns true, else false if invalid"""
        piece: Piece = self[old]
        if False in self.valid or Piece.get(piece) is None or not old.is_valid() or not new.is_valid():
            return False
        if not self[old] == piece:
            return False

        # Check if the move is generally valid
        if not new in self.get_valid_moves(piece, old):
            return False

        return True

    def print_board(self) -> str:
        """Pretty print the board"""
        ret: str = f'{str(self)}\nValid:{str(self.valid[0])}\n'
        if not self.valid[1]:
            return ret
        for i in range(7, -1, -1):
            for piece in self.rows[i]:
                ret += f'│\033[4m{str(piece)}\033[0m'
            ret += '│\n'
        ret += f'{"W" if self.turns == "w" else "B"} to go\n'
        if self.castling != "-":
            ret += f'Castling: {self.castling}\n'
        if self.en_passant != "-":
            ret += f'En passant: {self.en_passant}\n'
        ret += f'Half move clock: {str(self.half_and_full_move_clock[0])}\n'
        ret += f'Full move number: {str(self.half_and_full_move_clock[1])}\n'
        return ret


class TestFenCases(unittest.TestCase):
    """
    unit tests to check the validity of the FEN code
    """

    validfens: list[str] = [
        # Examples presented on wikipedia
        "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
        "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
        "rnbqkbnr/pp1ppppp/8/2p5/4P3/8/PPPP1PPP/RNBQKBNR w KQkq c6 0 2",
        "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",
        "rnbqkbnr/pp1ppppp/8/2p5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",

        # Weird cases
        "7k/RRRRRRR1/RRRRRRR1/RRRRRRR1/RRRRRRR1/RRRRRRR1/RRRRRRR1/RRRRRRRK w - - 0 1",
        "QNQNQN1k/NQNQN1N1/QNQNQN1N/NQNQNQNQ/QNQNQNQN/NQNQNQNQ/QNQNQNQN/NQNQNQNK w - - 0 1",
    ]

    invalidfens: list[str] = [
        # Invalid strings
        "",
        "A",

        # Empty board
        "8/8/8/8/8/8/8/8 w - - 0 1",

        # Invalid row count
        "rnbqkbnr/pp1pppp/8/2R5/4P3/5N2/PPPP1PPP/RNBQKB1R b KQkq - 1 2",

        # Double queens, no kings
        "rnbqqbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQQBNR w KQkq - 0 1",

        # Double kings
        "rnbkkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBKKBNR w KQkq - 0 1",

        # Pawns on row 0 or 7
        "P6k/8/8/8/8/8/8/7K w - - 0 1",
        "7k/8/8/8/8/8/8/P6K w - - 0 1",

        # Adjacent kings
        "8/8/8/8/8/8/8/6kK w - - 0 1",
        "k7/1K6/8/8/8/8/8/8 w - - 0 1",
        "8/1k6/2K5/8/8/8/8/8 w - - 0 1"
    ]

    def test_default(self):
        """Test default FENs"""
        local_fen: FEN = FEN()
        board: str = local_fen.print_board()
        self.assertTrue(local_fen.valid[0], board)
        self.assertEqual(
            local_fen.get_fen(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", board)

    def test_valid(self):
        """Test known valid FENs"""
        for fen in self.validfens:
            local_fen: FEN = FEN(fen)
            board: str = local_fen.print_board()
            self.assertTrue(local_fen.valid[0], board)
            self.assertEqual(local_fen.get_fen(), fen, board)

    def test_invalid(self):
        """Test invalid FENs"""
        for fen in self.invalidfens:
            local_fen: FEN = FEN(fen)
            board: str = local_fen.print_board()
            self.assertFalse(local_fen.valid[0], board)
            self.assertEqual(local_fen.get_fen(), fen, board)

    def test_indexing(self):
        """Test indexing into a FEN code"""
        fen: FEN = FEN()
        expected = Piece.WR
        actual = fen[Coordinates(0, 0)]
        self.assertEqual(expected, actual, f'Expected: {expected}\n'
                         f'Actual: {actual}')
        expected = Piece.BR
        actual = fen["a7"]
        self.assertEqual(expected, actual, f'Expected: {expected}\n'
                         f'Actual: {actual}')
        expected = fen["a"]
        actual = numpy.array([Piece.WR, Piece.WP,
                              Piece.NONE, Piece.NONE, Piece.NONE, Piece.NONE, Piece.BP, Piece.BR])
        self.assertTrue(numpy.array_equal(expected, actual), f'Expected: {expected}\n'
                        f'Actual: {actual}')
        expected = fen["7"]
        actual = numpy.array([Piece.BR, Piece.BN,
                              Piece.BB, Piece.BQ, Piece.BK, Piece.BB, Piece.BN, Piece.BR])
        self.assertTrue(numpy.array_equal(expected, actual), f'Expected: {expected}\n'
                        f'Actual: {actual}')


if __name__ == "__main__":
    unittest.main()
