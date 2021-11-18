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
        self._grid: "list[list[Piece]]" = [[Piece.NONE] * 8 for _ in range(8)]
        # This variable is used to tell which pawn is able to be en passant'ed. It should have
        # one of the elements be modified if a pawn moves up two places, and all reset to False
        # after each turn.
        self._en_passant_files: "list[bool]" = [False] * 8
        # 4 possible castling moves that are possible at the start of the game
        self._castle_white_king: bool = True
        self._castle_white_queen: bool = True
        self._castle_black_king: bool = True
        self._castle_black_queen: bool = True

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

    def yield_king(self, player: Player) -> Coordinates:
        """Yields all the coordinates of the players king"""
        king_piece = Piece.WK if player == Player.P1 else Piece.BK
        for file in range(8):
            for rank in range(8):
                coord = Coordinates(file, rank)
                if self[coord] == king_piece:
                    yield coord

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
            if capture_coords.is_valid() and self._en_passant_files[capture_coords.file]:
                if self[capture_coords] == Piece.NONE and player == Player.P1 and (
                        coords.rank == 4 or player == Player.P2 and coords.rank == 3):
                    valid_moves.append(capture_coords)

        return sorted(valid_moves)

    def __test_coords_empty(self, coords: "tuple[Coordinates, Coordinates]") -> bool:
        """Tests if the coordinates are all empty"""
        return all(not self[y] for y in coords)

    def __test_coords_check(self, king_coord: Coordinates, player: Player,
                            coords: "tuple[Coordinates, Coordinates]") -> bool:
        """Tests if any of the coords results in a check"""
        for king_pos in coords:
            copy = deepcopy(self)
            copy[king_coord] = Piece.NONE
            copy[king_pos] = Piece.WK if player == Player.P1 else Piece.BK
            if copy.is_in_check(player):
                return False
        return True

    def test_king_castling(self, player: Player) -> bool:
        """Test if player can castle on kingside"""
        if player == Player.P1 and not self._castle_white_king:
            return False
        if player == Player.P2 and not self._castle_black_king:
            return False
        empty_coords: "tuple[Coordinates, Coordinates]" = (
            Coordinates(5, 0), Coordinates(6, 0)
        ) if player == Player.P1 else (
            Coordinates(5, 7), Coordinates(6, 7)
        )
        # King side and Tiles between must be empty
        if not self.__test_coords_empty(empty_coords):
            return False
        test_coords: "tuple[Coordinates, Coordinates]" = (
            Coordinates(4, 0), Coordinates(5, 0), Coordinates(6, 0)
        ) if player == Player.P1 else (
            Coordinates(4, 7), Coordinates(5, 7), Coordinates(6, 7)
        )
        return self.__test_coords_check(
            Coordinates(4, 0) if player == Player.P1 else Coordinates(4, 7),
            player,
            test_coords)

    def test_queen_castling(self, player: Player) -> bool:
        """Test if player can castle on queenside"""
        if player == Player.P1 and not self._castle_white_queen:
            return False
        if player == Player.P2 and not self._castle_black_queen:
            return False
        empty_coords: "tuple[Coordinates, Coordinates]" = (
            Coordinates(3, 0), Coordinates(2, 0), Coordinates(1, 0)
        ) if player == Player.P1 else (
            Coordinates(3, 7), Coordinates(2, 7), Coordinates(1, 7)
        )
        # Queen side and Tiles between must be empty
        if not self.__test_coords_empty(empty_coords):
            return False
        test_coords: "tuple[Coordinates, Coordinates]" = (
            Coordinates(4, 0), Coordinates(3, 0), Coordinates(2, 0)
        ) if player == Player.P1 else (
            Coordinates(4, 7), Coordinates(3, 7), Coordinates(2, 7)
        )
        return self.__test_coords_check(
            Coordinates(4, 0) if player == Player.P1 else Coordinates(4, 7),
            player,
            test_coords)

    def generate_legal_castle_moves(self, player: Player) -> "list[Coordinates]":
        """Generates the castle moves available for the player. This should be appended to the list
        of moves after pruning since this function does its own pruning since castling is
        complicated"""
        assert player in (Player.P1, Player.P2)

        funcs = {
            Player.P1: (
                # Rook and king placement are already correct because of _castle_white_king
                # The king must not be in check for any step along the way
                (self.test_king_castling(Player.P1), Coordinates(6, 0)),
                # Rook and king placement are already correct because of _castle_white_queen
                (self.test_queen_castling(Player.P1), Coordinates(2, 0)),
            ),
            Player.P2: (
                (self.test_king_castling(Player.P2), Coordinates(6, 7)),
                (self.test_queen_castling(Player.P2), Coordinates(2, 7)),
            ),
        }
        valid_moves = [coord for b, coord in funcs[player] if b]
        return valid_moves

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

        # The king lives another day if the following returns false
        return any([
            __check_knights(king_pos, player),
            __check_queens(king_pos, player),
            __check_rooks(king_pos, player),
            __check_bishops(king_pos, player),
            __check_pawns(king_pos, player),
            __check_king(king_pos, player)
        ])

    def move(self, from_coords: Coordinates, to_coords: Coordinates, player: Player) -> None:
        """Moves a piece from one location to another"""
        assert from_coords.is_valid() and to_coords.is_valid()
        assert self[from_coords].is_on_side(player)
        self[to_coords] = self[from_coords]
        self[from_coords] = Piece.NONE

        rank: int = 0 if player == Player.P1 else 7
        file_diff: int = to_coords.file - from_coords.file

        # Handle moving the rooks if this is a castle move
        if abs(file_diff) == 2 and self[to_coords].is_king():
            self[Coordinates(7 if file_diff == 2 else 0, rank)] = Piece.NONE
            self[Coordinates(5 if file_diff == 2 else 3, rank)
                 ] = Piece.WR if player == Player.P1 else Piece.BR

        # If we performed en passant, we need to remove the pawn
        if self[to_coords].is_pawn() and abs(to_coords.file - from_coords.file) == 1:
            if self._en_passant_files[to_coords.file] and to_coords.rank == 2:
                self[Coordinates(to_coords.file, 3)] = Piece.NONE
            if self._en_passant_files[to_coords.file] and to_coords.rank == 5:
                self[Coordinates(to_coords.file, 4)] = Piece.NONE

        # Clear en passant flags
        self._en_passant_files = [False] * 8

        # If we move a pawn up two spaces we need to set its en_passant flag
        if abs(to_coords.rank - from_coords.rank) == 2 and self[to_coords].is_pawn():
            self._en_passant_files[to_coords.file] = True

        # Moving the king will always revoke both castling rights
        if self[to_coords].is_king():
            if player == Player.P1:
                self._castle_white_king, self._castle_white_queen = False, False
            else:
                self._castle_black_king, self._castle_black_queen = False, False
            return

        # Revoke castling rights if they move the king or rook
        if player == Player.P1:
            # Moving a piece from the corner of the board will revoke a castling right. It doesn't
            # matter if it isn't a rook, since we only have to revoke rights once then they are
            # gone for good.
            self._castle_white_queen = False if from_coords == "a1" else self._castle_white_queen
            self._castle_white_king = False if from_coords == "h1" else self._castle_white_king
            # If we capture the opposing squares, we revoke the opponent's castling rights
            self._castle_black_queen = False if to_coords == "a8" else self._castle_black_queen
            self._castle_black_king = False if to_coords == "h8" else self._castle_black_king
            return

        # Same thing as above but flipped
        self._castle_black_queen = False if from_coords == "a8" else self._castle_black_queen
        self._castle_black_king = False if from_coords == "h8" else self._castle_black_king
        # If we capture the opposing squares, we revoke the opponent's castling rights
        self._castle_white_queen = False if to_coords == "a1" else self._castle_white_queen
        self._castle_white_king = False if to_coords == "h1" else self._castle_white_king

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
