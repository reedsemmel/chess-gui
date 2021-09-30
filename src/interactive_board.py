"""
File: interactive_board.py
Author: Reed Semmel
Date: 2021-09-26
Description:
    Classes and widgets for the interactive game board.
"""


from enum import Enum, unique
from PyQt5 import QtGui
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget

@unique
class Piece(Enum):
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

    def __init__(self) -> None:
        super().__init__()

        # Load up all the assets we need
        # TODO: Fix these piece images to be exactly square
        self.piece_img = {
            Piece.NONE: QtGui.QPixmap("assets/blank.png"),
            Piece.WR: QtGui.QPixmap("assets/wr.png"),
            Piece.WB: QtGui.QPixmap("assets/wb.png"),
            Piece.WN: QtGui.QPixmap("assets/wn.png"),
            Piece.WQ: QtGui.QPixmap("assets/wq.png"),
            Piece.WK: QtGui.QPixmap("assets/wk.png"),
            Piece.WP: QtGui.QPixmap("assets/wp.png"),
            Piece.BR: QtGui.QPixmap("assets/br.png"),
            Piece.BB: QtGui.QPixmap("assets/bb.png"),
            Piece.BN: QtGui.QPixmap("assets/bn.png"),
            Piece.BQ: QtGui.QPixmap("assets/bq.png"),
            Piece.BK: QtGui.QPixmap("assets/bk.png"),
            Piece.BP: QtGui.QPixmap("assets/bp.png"),
        }
        
        # Set up an 8 by 8 grid
        layout = QGridLayout(self)
        layout.setSpacing(0)

        self.tileGrid = [[self.ChessTile(i, j) for i in range(8)] for j in range(8)]
        for i in range(8):
            for j in range(8):
                layout.addWidget(self.tileGrid[i][j], i, j)

        self.setLayout(layout)
    
    # Called by ChessTile widgets and passes their position to this function
    def handleClick(self, x: int, y: int) -> None:
        """Handles a click from the user
        
        Called by a tile once it is clicked. The tile provides the arguments
        x and y from its position on the grid
        """
        # Dummy implementation for now. Just for testing
        print("Tile", x, y, "clicked")
    
    # Replaces the piece on (x,y) with the piece name from the piece_img array
    def drawPiece(self, piece: Piece, x: int, y: int) -> None:
        """Draws and replaced a piece on the board"""
        if 0 <= x <= 7 and 0 <= y <= 7:
            self.tileGrid[y][x].setImage(self.piece_img[piece])
        else:
            print(f"Invalid index {x} {y}")
    
    class ChessTile(QWidget):
        """A basic chess tile widget

        A simple widget which holds nothing but a piece image and forwards
        clicks to the parent.
        """
        # TODO: add a resize event to redraw the pixmaps at a corrected size
        def __init__(self, x: int, y: int) -> None:
            super().__init__()
            self.x = x
            self.y = y
            # Holds the image we display
            self.label = QLabel(self)

            # TODO: pick less ugly colors
            # Chess is played on a checkered board. Adding the x and y index is an
            # easy way to see which we are on
            if ((self.x + self.y) % 2):
                self.setStyleSheet("background-color: #573D11;")
            else:
                self.setStyleSheet("background-color: #DCB167;")

        def setImage(self, piece: QtGui.QPixmap):
            self.label.setPixmap(piece)

        def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
            self.parentWidget().handleClick(self.x, self.y)

# Basic testing code

if (__name__ == "__main__"):
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = InteractiveBoard()

    defaultBoard = [[Piece.NONE for _ in range(8)] for _ in range(8)]
    defaultBoard[2][3] = Piece.WR
    for i in range(8):
        for j in range(8):
            widget.drawPiece(defaultBoard[i][j], i, j)

    widget.setGeometry(0, 0, 1000, 1000)
    widget.show()
    app.exec_()
