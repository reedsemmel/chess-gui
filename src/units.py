#!/usr/bin/env python3

# Copyright (c) 2021 Alishan Bhayani, Reed Semmel, Chris Degawa
# SPDX-License-Identifier: GPL-3.0-only

"""
File: units.py
Author: Christopher Degawa
Date: 11/18/2021
Description:
    Holds all of the unit tests

"""

import unittest

from board import Board
from utils import Coordinates, Piece, Player, Settings

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

        def test_basic_castling(self):
            """Tests basic king side castling for both sides"""
            board = Board().new_default_board()
            # Standard start to the game to allow both sides to king side castle.
            board.move(Coordinates("e2"), Coordinates("e4"), Player.P1)
            board.move(Coordinates("e7"), Coordinates("e5"), Player.P2)
            board.move(Coordinates("g1"), Coordinates("f3"), Player.P1)
            board.move(Coordinates("g8"), Coordinates("f6"), Player.P2)
            board.move(Coordinates("f1"), Coordinates("e2"), Player.P1)
            board.move(Coordinates("f8"), Coordinates("e7"), Player.P2)
            # Now both sides are able to castle king side.
            self.assertTrue(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            board.move(Coordinates("e1"), Coordinates("g1"), Player.P1)
            self.assertTrue(Coordinates(
                "g8") in board.generate_legal_castle_moves(Player.P2))

        def test_basic_queen_side_castling(self):
            """Tests basic queen side castling for both sides"""
            board = Board().new_default_board()
            # Standard start to the game to allow both sides to queen side castle.
            board.move(Coordinates("d2"), Coordinates("d4"), Player.P1)
            board.move(Coordinates("d7"), Coordinates("d5"), Player.P2)
            board.move(Coordinates("d1"), Coordinates("d3"), Player.P1)
            board.move(Coordinates("d8"), Coordinates("d6"), Player.P2)
            board.move(Coordinates("c1"), Coordinates("e3"), Player.P1)
            board.move(Coordinates("c8"), Coordinates("e6"), Player.P2)
            board.move(Coordinates("b1"), Coordinates("a3"), Player.P1)
            board.move(Coordinates("b8"), Coordinates("a6"), Player.P2)
            # Now both sides are able to castle queen side.
            self.assertTrue(Coordinates(
                "c1") in board.generate_legal_castle_moves(Player.P1))
            board.move(Coordinates("e1"), Coordinates("c1"), Player.P1)
            self.assertTrue(Coordinates(
                "c8") in board.generate_legal_castle_moves(Player.P2))

        def test_castling_revoke_rook(self):
            """Tests moving a rook and moving it back to see if it properly revokes castling"""
            board = Board().new_default_board()
            # Start to allow white to move rook then attempt castling.
            board.move(Coordinates("e2"), Coordinates("e3"), Player.P1)
            board.move(Coordinates("b8"), Coordinates("a6"), Player.P2)
            board.move(Coordinates("h2"), Coordinates("h3"), Player.P1)
            board.move(Coordinates("a6"), Coordinates("b8"), Player.P2)
            board.move(Coordinates("f1"), Coordinates("e2"), Player.P1)
            board.move(Coordinates("b8"), Coordinates("a6"), Player.P2)
            board.move(Coordinates("g1"), Coordinates("f3"), Player.P1)
            board.move(Coordinates("a6"), Coordinates("b8"), Player.P2)
            # White king should be able to castle
            self.assertTrue(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            # Move rook out of the way
            board.move(Coordinates("h1"), Coordinates("h2"), Player.P1)
            board.move(Coordinates("b8"), Coordinates("a6"), Player.P2)
            # Now white king should not be able to castle
            self.assertFalse(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            # Move rook back
            board.move(Coordinates("h2"), Coordinates("h1"), Player.P1)
            board.move(Coordinates("a6"), Coordinates("b8"), Player.P2)
            # White king should still not be able to castle
            self.assertFalse(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))

        def test_castling_revoke_king(self):
            """Tests moving a king to see if it revokes castling"""
            board = Board().new_default_board()
            board.move(Coordinates("e2"), Coordinates("e3"), Player.P1)
            board.move(Coordinates("b8"), Coordinates("a6"), Player.P2)
            board.move(Coordinates("h2"), Coordinates("h3"), Player.P1)
            board.move(Coordinates("a6"), Coordinates("b8"), Player.P2)
            board.move(Coordinates("f1"), Coordinates("d3"), Player.P1)
            board.move(Coordinates("b8"), Coordinates("a6"), Player.P2)
            board.move(Coordinates("g1"), Coordinates("f3"), Player.P1)
            board.move(Coordinates("a6"), Coordinates("b8"), Player.P2)
            # White king should be able to castle
            self.assertTrue(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            # Move king out of the way
            board.move(Coordinates("e1"), Coordinates("e2"), Player.P1)
            board.move(Coordinates("b8"), Coordinates("a6"), Player.P2)
            # Now white king should not be able to castle
            self.assertFalse(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            # Move king back
            board.move(Coordinates("e2"), Coordinates("e1"), Player.P1)
            board.move(Coordinates("a6"), Coordinates("b8"), Player.P2)
            # White king should still not be able to castle
            self.assertFalse(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))

        def test_castling_in_check(self):
            """Tests to make sure you can't castle while in check, and any spots you pass while
            castling"""
            board = Board().new_default_board()
            # Remove all pieces in the way and spawn a queen lol
            board[Coordinates("e2")] = Piece.NONE
            board[Coordinates("f2")] = Piece.NONE
            board[Coordinates("g2")] = Piece.NONE
            board[Coordinates("h2")] = Piece.NONE
            board[Coordinates("f1")] = Piece.NONE
            board[Coordinates("g1")] = Piece.NONE

            self.assertTrue(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))

            board[Coordinates("e5")] = Piece.BQ
            # King is in check by the queen, so castling should be impossible
            self.assertFalse(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            # Move queen to the right. The king can still not castle since it would be put in check
            # while moving to g1.
            board.move(Coordinates("e5"), Coordinates("f5"), Player.P2)
            self.assertFalse(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            # Move queen to the right again. Still should not be able to castle since castling would
            # put the king in check.
            board.move(Coordinates("f5"), Coordinates("g5"), Player.P2)
            self.assertFalse(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))
            # Remove queen. Can castle now
            board.move(Coordinates("g5"), Coordinates("h5"), Player.P2)
            self.assertTrue(Coordinates(
                "g1") in board.generate_legal_castle_moves(Player.P1))

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
            for each in ("This! is! invalid!",):
                self.settings.configurables["player_name"]["handle_func"](each)
                self.assertEqual(self.settings.player_name, "Player 1",
                                 "Player name was changed from \"Player 1\""
                                 f" to \"{self.settings.player_name}\"")

                self.settings.configurables["opponent_name"]["handle_func"](
                    each)
                self.assertEqual(self.settings.opponent_name, "Player 2",
                                 f"Player name was changed from \"Player 2\" to \"{self.settings.opponent_name}\"")  # pylint: disable=line-too-long

        def test_invalid_color_changes(self) -> None:
            """Tests that invalid colors are rejected."""
            for each in ("#invali", "#dhexes", "#12345!"):
                self.settings.configurables["primary_color"]["handle_func"](
                    each)
                self.assertEqual(self.settings.primary_color, "#573D11",
                                 "Primary color was changed from #573D11"
                                 f" to {self.settings.primary_color}")

                self.settings.configurables["secondary_color"]["handle_func"](
                    each)
                self.assertEqual(self.settings.secondary_color, "#DCB167",
                                 "Secondary color was changed from #DCB167"
                                 f" to {self.settings.secondary_color}")

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
            for each in ("This is valid 123",):
                self.settings.configurables["player_name"]["handle_func"](each)
                self.assertEqual(self.settings.player_name, each,
                                 f"Failed to change player name from \"Player 1\" to \"{each}\"")

                self.settings.configurables["opponent_name"]["handle_func"](
                    each)
                self.assertEqual(self.settings.opponent_name, each,
                                 f"Failed to change opponent name from \"Player 2\" to \"{each}\"")

        def test_valid_color_changes(self):
            """Tests that valid colors are accepted."""
            for each in ("#123456", "#cf3445", "#FFF"):
                self.settings.configurables["primary_color"]["handle_func"](
                    each)
                self.assertEqual(self.settings.primary_color, each,
                                 f"Failed to change primary color from #573D11 to {each}")

                self.settings.configurables["secondary_color"]["handle_func"](
                    each)
                self.assertEqual(self.settings.secondary_color, each,
                                 f"Failed to change secondary color from #DCB167 to {each}")

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
