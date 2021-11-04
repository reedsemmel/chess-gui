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

from typing import Union
from board import Board
from utils import Piece, Coordinates, Player


class FEN:
    """
    Class to hold and interpret a FEN code

    valid: tuple[bool, bool] first is used to check if the FEN code is valid
                             the second is used to check if the board is valid
                             and can be printed

    The later fields are only valid if valid[0] is True

    board: Board the chess board, indexed by Coordinates
    turns: Player the player to go next
    castling: str the castling rights
    en_passant: str the en passant square
    half_and_full_move_clock: tuple[int, int] the half move and full move clock
    str(FEN): str returns the FEN code

    a board is considered valid if the analysis board button is
    available at https://lichess.org/editor, excluding checks and mates

    """

    @staticmethod
    def __check_syntax(fields: "list[str]", rows: "list[list[Piece]]") -> bool:
        """Basic syntax checks"""

        def __check_row(row: "list[Piece]") -> bool:
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

    @staticmethod
    def __check_board(board: Board) -> bool:
        """Chess piece checks"""

        # Each side can only have 1 king
        if len(list(board.yield_king(Player.P1)) + list(board.yield_king(Player.P2))) != 2:
            return False

        # Pawn on row 0 or 7 check
        for i in (0, 7):
            for j in range(8):
                if board[Coordinates(j, i)] in (Piece.BP, Piece.WP):
                    return False

        # Opposing kings can't be next to nor diagonal from each other
        for coord in Piece.get_valid_king_moves(board.find_king(Player.P1)):
            if Piece.BK == board[coord]:
                return False
        return True

    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """Initalize and verify a FEN, default fen is the default chess board"""

        self.valid: "tuple[bool, bool]" = (False, False)
        self.board: Board = Board.new_empty_board()
        self.turns: Player = Player.P1
        self.castling: str = ""
        self.en_passant: str = ""
        self.half_and_full_move_clock: "tuple[int, int]" = (0, 0)

        # Fen code as we received it if we need to print an error
        self.__fen: str = fen

        fields: "list[str]" = list(
            filter("".__ne__, fen.strip().split(" ")))

        if len(" ".join(fields)) == 0:
            return

        rows: "list[list[Piece]]" = []
        for row in reversed(fields[0].split("/")):
            curr_row: "list[Piece]" = []
            for char in row:
                if char.isdigit():
                    curr_row += [Piece.NONE] * int(char)
                elif char.lower() in "prbnqk":
                    curr_row.append(Piece.str_to_piece(char))
            rows.append(curr_row)

        for rank, row in enumerate(rows):
            for file, piece in enumerate(row):
                self.board[Coordinates(file, rank)] = piece

        if FEN.__check_syntax(fields, rows) is False:
            return

        self.valid: "tuple[bool, bool]" = (False, True)
        self.turns: Player = Player.P1 if fields[1].lower() == "w" else Player.P2
        self.castling: str = fields[2]
        self.en_passant: str = fields[3]
        self.half_and_full_move_clock: "tuple[int, int]" = (
            int(fields[4]), int(fields[5]))

        if FEN.__check_board(self.board) is False:
            return

        self.valid: "tuple[bool, bool]" = (True, True)

    def get_fen(self) -> str:
        """Get the FEN code"""
        if not self.valid[0]:
            return self.__fen
        board: str = ""

        for rank in range(7, -1, -1):
            count: int = 0
            for file in range(8):
                piece: Piece = self.board[Coordinates(file, rank)]
                if piece == Piece.NONE:
                    count += 1
                    continue
                if count != 0:
                    board += str(count)
                    count = 0
                board += str(piece)
            if count != 0:
                board += str(count)
            if rank != 0:
                board += "/"

        return " ".join([
            board,
            "w" if self.turns == Player.P1 else "b",
            self.castling,
            self.en_passant,
            str(self.half_and_full_move_clock[0]),
            str(self.half_and_full_move_clock[1])
        ])

    def __str__(self) -> str:
        return self.get_fen()

    def __getitem__(self, key: Union[str, Coordinates]) -> Piece:
        """
        Returns piece.
        Can be indexed using Coordinates or a string of the form "a1"
        """

        if isinstance(key, Coordinates):
            return self.board[key]
        if isinstance(key, str) and len(key) == 2 and key[0].lower() in "abcdefg" \
                and int(key[1]) in range(1, 9):
            return self.board[Coordinates(key)]
        return Piece.NONE

    def print_board(self) -> str:
        """Pretty print the board"""
        ret: str = f"{self}\nValid:{self.valid[0]}\n"
        if not self.valid[1]:
            return ret
        for rank in range(7, -1, -1):
            for file in range(8):
                ret += f"│\033[4m{self.board[Coordinates(file, rank)]}\033[0m"
            ret += "│\n"
        ret += f"{'W' if self.turns == Player.P1 else 'B'} to go\n"
        if self.castling != "-":
            ret += f"Castling: {self.castling}\n"
        if self.en_passant != "-":
            ret += f"En passant: {self.en_passant}\n"
        ret += f"Half move clock: {self.half_and_full_move_clock[0]}\n"
        ret += f"Full move number: {self.half_and_full_move_clock[1]}\n"
        return ret


if __name__ == "__main__":
    import unittest

    class TestFenCases(unittest.TestCase):
        """unit tests to check the validity of the FEN code"""

        validfens: "list[str]" = [
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

        invalidfens: "list[str]" = [
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
                local_fen.get_fen(), "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
                board)

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
            actual = fen["a8"]
            self.assertEqual(expected, actual, f'Expected: {expected}\n'
                             f'Actual: {actual}')

    unittest.main()
