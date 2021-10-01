#!/usr/bin/env python
import unittest

__author__ = "Christopher Degawa"
__license__ = "GPL-3.0-or-later"
__version__ = "0.0.1"
__contact__ = "cdegawa@vols.utk.edu"
__date__ = "9/27/2021"


class FEN:
    """
    Class to hold and interpret a FEN code

    valid: bool used to check if the FEN code is valid

    The later fields are only valid if valid is True

    board_valid: bool used to check if the board is valid, used to check
        if the board can be printed

    rows: tuple[str, ...] the rows of the chess board, can index using [0-7][0-7]
    turns: str the color to go next
    castling: str the castling rights
    en_passant: str the en passant square
    half_move_clock: int the half move clock
    full_move_number: int the full move number
    str(FEN): str returns the FEN code

    a board is considered valid if the analysis board button is
    available at https://lichess.org/editor, excluding checks and mates

    """

    @staticmethod
    def __check_syntax(fields: list[str], rows: list[str]) -> bool:
        """Basic syntax checks"""

        def __check_row(row: str) -> bool:
            """Check a row for validity"""

            if len(row) != 8:
                return False
            for c in row:
                if not c.upper() in " PRNBQK":
                    return False
            return True

        if len(fields) != 6:
            return False
        if len(rows) != 8:
            return False
        for row in rows:
            if not __check_row(row):
                return False

        """Check turns field"""
        if len(fields[1]) != 1 and fields[1].lower() not in "wb":
            return False
        """Check castling field"""
        if False in [x in "-kq" for x in fields[2].lower()]:
            return False
        """Check en passant field"""
        if not fields[3].lower()[0] in "-abcdefgh":
            return False
        if len(fields[3]) == 2 and fields[3][1] not in "12345678":
            return False
        """Check half move clock field and full move clock field"""
        if not fields[4].isdigit() or not fields[5].isdigit():
            return False
        return True

    @staticmethod
    def __check_board(fields: list[str], rows: list[str]) -> bool:
        """Chess piece checks"""

        """Each side can only have 1 king"""
        if fields[0].count("k") != 1 or fields[0].count("K") != 1:
            return False

        """Pawn on row 0 or 7 check"""
        if rows[0].count("p") or rows[0].count("P") or rows[7].count("p") or rows[7].count("P"):
            return False

        """Opposing kings can't be next to nor diagonal from each other"""
        rows_concatinated: str = "".join(rows)
        i: int = int(rows_concatinated.index("k") / 8)
        j: int = rows_concatinated.index("k") % 8
        if i > 0 and rows[i - 1][j].lower() == "k":
            return False
        if i < 7 and rows[i + 1][j].lower() == "k":
            return False
        if j > 0 and rows[i][j - 1].lower() == "k":
            return False
        if j < 7 and rows[i][j + 1].lower() == "k":
            return False
        if i > 0 and j > 0 and rows[i - 1][j - 1].lower() == "k":
            return False
        if i > 0 and j < 7 and rows[i - 1][j + 1].lower() == "k":
            return False
        if i < 7 and j > 0 and rows[i + 1][j - 1].lower() == "k":
            return False
        if i < 7 and j < 7 and rows[i + 1][j + 1].lower() == "k":
            return False
        return True

    def __init__(self, fen: str = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"):
        """Initalize and verify a FEN, default fen is the default chess board"""

        self.valid: bool = False
        self.board_valid: bool = False
        self.rows: tuple[str, ...] = ()
        self.turns: str = ""
        self.castling: str = ""
        self.en_passant: str = ""
        self.half_move_clock: int = 0
        self.full_move_number: int = 0

        fields: "list[str]" = list(
            filter("".__ne__, fen.strip().split(" ")))
        self.__fen: str = " ".join(fields)

        if len(self.__fen) == 0:
            return

        rows: "list[str]" = ["".join(
            [x if x.isalpha() else " " * int(x) for x in row]) for row in fields[0].split("/")]

        if FEN.__check_syntax(fields, rows) is False:
            return

        self.board_valid: bool = True
        self.rows: tuple(str, ...) = tuple(rows)
        self.turns: str = fields[1]
        self.castling: str = fields[2]
        self.en_passant: str = fields[3]
        self.half_move_clock: int = int(fields[4])
        self.full_move_number: int = int(fields[5])

        if FEN.__check_board(fields, rows) is False:
            return

        self.valid: bool = True

    def __str__(self) -> str:
        return self.__fen

    def __getitem__(self, key) -> str:
        """
        Returns either the row or piece.
        Can be indexed using 1-8 or a-h or using algebraic notation a8
        """
        if (type(key) is int or key.isdigit()) and int(key) in range(1, 9):
            return self.rows[8 - int(key)]
        if not type(key) is str:
            return ""
        if len(key) == 1 and key[0].lower() in "abcdefg":
            return "".join([self.rows[x][ord(key) - ord("a")] for x in range(8)])
        if len(key) == 2 and key[0].lower() in "abcdefg" and int(key[1]) in range(1, 9):
            return self.__getitem__(key[0].lower())[8 - int(key[1])]
        return ""

    def print_board(self) -> str:
        ret: str = self.__fen + "\n" + "Valid: " + str(self.valid) + "\n"
        if not self.board_valid:
            return ret
        for i in range(8):
            for piece in self.rows[i]:
                ret += "│\033[4m{}\033[0m".format(piece)
            ret += "│\n"
        ret += "W to go\n" if self.turns == "w" else "B to go\n"
        if self.castling != "-":
            ret += "Castling: " + self.castling + "\n"
        if self.en_passant != "-":
            ret += "En passant: " + self.en_passant + "\n"
        ret += "Half move clock: " + str(self.half_move_clock) + "\n"
        ret += "Full move number: " + str(self.full_move_number) + "\n"
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
        localfen: FEN = FEN()
        print(localfen.print_board())
        self.assertTrue(localfen.valid)

    def test_valid(self):
        for fen in self.validfens:
            localfen: FEN = FEN(fen)
            print(localfen.print_board())
            self.assertTrue(localfen.valid)

    def test_invalid(self):
        for fen in self.invalidfens:
            localfen: FEN = FEN(fen)
            print(localfen.print_board())
            self.assertFalse(localfen.valid)

    def test_indexing(self):
        self.assertEqual(FEN()["a8"], "r")
        self.assertEqual(FEN()["a"], "rp    PR")
        self.assertEqual(FEN()["8"], "rnbqkbnr")


if __name__ == "__main__":
    unittest.main()
