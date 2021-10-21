#!/usr/bin/env python3

# Copyright (c) 2021 Reed Semmel
# SPDX-License-Identifier: GPL-3.0-only

"""
File: interactive_board.py
Author: Reed Semmel
Date: 2021-10-04
Description:
    Classes and widgets for the interactive game board.
"""

from typing import List
from PyQt5 import QtGui
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget

from utils import Piece, Settings, Coordinates
from chess import Chess

class InteractiveBoard(QWidget):
    """An interactive chess board widget.

    This widget will draw a basic chess board, though it is useless by itself.
    There is no underlying engine or logic. It just draws the pieces and lets
    you click on the tiles, which triggers a function. This must be interfaced
    with a backend logic to become complete.
    This widget imposes no restrictions on geometry. The parent MUST ensure that
    this widget remains a square exactly pixel by pixel, otherwise the drawing
    will be off.
    """

    def __init__(self, chess: Chess, settings: Settings) -> None:
        super().__init__()
        self.chess = chess
        self.current_selection: Coordinates = Coordinates(-1, -1)


        # Set up an 8 by 8 grid
        layout = QGridLayout(self)
        layout.setSpacing(0)

        self.tile_grid = [[self.ChessTile(file, rank, settings) for rank in range(8)]
            for file in range(8)]
        for file in range(8):
            for rank in range(8):
                # Rank is the row, File is the column.
                # Additionally, show the 1st rank on the bottom. (White's view)
                # (Black's view would be (rank, 8 - file))
                layout.addWidget(self.tile_grid[file][rank], 8 - rank, file)
                # We also want to set the blank background so the CSS background
                # colors properly show up.
                self.tile_grid[file][rank].set_image(Piece.NONE)

        self.setLayout(layout)
        self.redraw_whole_board(self.chess.get_state().board._grid)

    # Called by ChessTile widgets and passes their position to this function
    def handle_click(self, file: int, rank: int) -> None:
        """Handles a click from the user

        Called by a tile once it is clicked. The tile provides the arguments
        x and y from its position on the grid
        """

        coord: Coordinates = Coordinates(file, rank)


        # If a tile isn't selected, select it
        if not self.current_selection.is_valid():
            if self.chess.piece_at(coord).is_on_side(self.chess.state.current_turn):
                print(coord, ":", self.chess.get_valid_moves(coord))
                for tile in self.chess.get_valid_moves(coord):
                    self.tile_grid[tile.file][tile.rank].highlight_green()
                self.current_selection = coord
            else:
                print("that tile doesn't have one of the current turn's pieces on it")
        else:
            if self.chess.check_move(self.current_selection, coord):
                self.chess.make_move(self.current_selection, coord)
                self.redraw_whole_board(self.chess.get_state().board._grid)
            self.current_selection = Coordinates(-1, -1)
            for file in self.tile_grid:
                for tile in file:
                    tile.remove_highlight()


    # Replaces the piece on (file, rank) with the piece provided
    def draw_piece(self, piece: Piece, file: int, rank: int) -> None:
        """Draws and replaced a piece on the board"""
        if file in range(0, 8) and rank in range(0, 8):
            self.tile_grid[file][rank].set_image(piece)
        else:
            print(f"Invalid index {file} {rank}")

    def redraw_whole_board(self, board: List[List[Piece]]) -> bool:
        """Redraws the whole board from an 8x8 grid of pieces"""

        # Ensure it is 8x8
        if len(board) != 8:
            return False
        for file in board:
            if len(file) != 8:
                return False

        for file_index, file in enumerate(board):
            for rank_index, cell in enumerate(file):
                self.draw_piece(cell, file_index, rank_index)

        return True



    class ChessTile(QWidget):
        """A basic chess tile widget

        A simple widget which holds nothing but a piece image and forwards
        clicks to the parent.
        """
        def __init__(self, file: int, rank: int, settings: Settings) -> None:
            super().__init__()
            self.file = file
            self.rank = rank
            # Holds the image we display
            self.label = QLabel(self)
            self.current_piece = Piece.NONE

            # Chess is played on a checkered board. Adding the file and rank
            # index is an easy way to see which we are on
            if (self.file + self.rank) % 2:
                self.color = settings.secondary_color
            else:
                self.color = settings.primary_color

            self.setStyleSheet(f"background-color: {self.color};")

        def highlight_green(self):
            self.setStyleSheet("background-color: #22dd22;")

        def highlight_red(self):
            self.setStyleSheet("background-color: #dd2222;")

        def remove_highlight(self):
            self.setStyleSheet(f"background-color: {self.color};")

        def set_image(self, piece: Piece):
            """Sets the image in the tile to the one provided."""
            if piece == self.current_piece:
                return
            self.current_piece = piece
            self.adjustSize()
            self.label.setPixmap(Piece.get_piece_pixmap(self.current_piece).scaled(self.size()))

        def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None: # pylint: disable=invalid-name
            """Passes the click information to the parent widget along with the rank and file."""
            self.parentWidget().handle_click(self.file, self.rank)

        # There is almost certainly a more efficient way to do this, but it is
        # fast enough and doesn't cause noticeable artifacts when resizing
        def resizeEvent(self, a0: QtGui.QResizeEvent) -> None: # pylint: disable=invalid-name
            """Resizes the label and image to fill the entire widget upon resizing"""
            if a0.size().height() == 0 or a0.size().width() == 0:
                return
            self.label.setPixmap(Piece.get_piece_pixmap(self.current_piece).scaled(a0.size()))
            self.label.adjustSize()
            self.adjustSize()

# Basic testing code

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    app = QApplication(sys.argv)

    widget = InteractiveBoard(Chess(), Settings())
    widget.setGeometry(0, 0, 800, 800)
    widget.show()

    app.exec_()
