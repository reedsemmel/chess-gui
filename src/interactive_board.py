"""
File: interactive_board.py
Author: Reed Semmel
Date: 2021-09-26
Description:
    Classes and widgets for the interactive game board.
"""

from PyQt5 import QtGui
from PyQt5.QtWidgets import QGridLayout, QLabel, QWidget

"""An interactive chess board widget.

This widget will draw a basic chess board, though it is useless by itself. There
is no underlying engine or logic. It just draws the pieces and lets you click on
the tiles, which triggers a function. This must be interfaced with a backend
logic to become complete.
This widget imposes no restrictions on geometry. The parent MUST ensure that
this widget remains a square exactly pixel by pixel, otherwise the drawing will
be off.
"""
class InteractiveBoard(QWidget):
    def __init__(self) -> None:
        super().__init__()
        # Load up all the assets we need

        # TODO: Fix these piece images to be exactly square
        self.piece_img = {
            'wr': QtGui.QPixmap("assets/wr.png"),
            'wb': QtGui.QPixmap("assets/wb.png"),
            'wn': QtGui.QPixmap("assets/wn.png"),
            'wq': QtGui.QPixmap("assets/wq.png"),
            'wk': QtGui.QPixmap("assets/wk.png"),
            'wp': QtGui.QPixmap("assets/wp.png"),
            'br': QtGui.QPixmap("assets/br.png"),
            'bb': QtGui.QPixmap("assets/bb.png"),
            'bn': QtGui.QPixmap("assets/bn.png"),
            'bq': QtGui.QPixmap("assets/bq.png"),
            'bk': QtGui.QPixmap("assets/bk.png"),
            'bp': QtGui.QPixmap("assets/bp.png"),
            'none': QtGui.QPixmap("assets/blank.png")
        }
        
        # Set up an 8 by 8 grid
        layout = QGridLayout(self)
        layout.setSpacing(0)

        self.tileGrid = []

        # Create the 64 tiles and put them in a grid layout
        for i in range(8):
            self.tileGrid.append([])
            for j in range(8):
                self.tileGrid[i].append(ChessTile(i, j))
                layout.addWidget(self.tileGrid[i][j], i, j)
        self.setLayout(layout)
        print(self.tileGrid)
    
    #Called by ChessTile widgets and passes their position to this function
    def handleClick(self, x, y) -> None:
        # Dummy implementation for now. Just for testing
        print("Tile", x, y, "clicked")
    
    # Replaces the piece on (x,y) with the piece name from the piece_img array
    def drawPiece(self, piece: str, x: int, y: int) -> None:
        self.tileGrid[x][y].label.setPixmap(self.piece_img[piece])
"""A basic chess tile widget

A simple widget which holds nothing but a piece image and forwards clicks to
the parent.
"""
class ChessTile(QWidget):
    # TODO: add a resize event to redraw the pixmaps at a corrected size
    def __init__(self, x, y) -> None:
        super().__init__()
        self.x = x
        self.y = y
        # Holds the image we display
        self.label = QLabel(self)

        # TODO: pick less ugly colors
        # Chess is played on a checkered board. Adding the x and y index is an
        # easy way to see which we are on
        if ((self.x + self.y) % 2):
            self.setStyleSheet("background-color: #573D11")
        else:
            self.setStyleSheet("background-color: #DCB167")


    # Forward clicks from each child for the main widget to handle
    def mousePressEvent(self, a0: QtGui.QMouseEvent) -> None:
        self.parentWidget().handleClick(self.x, self.y)

# Basic testing code
if (__name__ == "__main__"):
    import sys
    from PyQt5.QtWidgets import QApplication
    app = QApplication(sys.argv)
    widget = InteractiveBoard()

    defaultBoard = [
        ['br', 'bn', 'bb', 'bq', 'bk', 'bb', 'bn', 'br'],
        ['bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp', 'bp'],
        ['none', 'none', 'none', 'none', 'none', 'none', 'none', 'none'],
        ['none', 'none', 'none', 'none', 'none', 'none', 'none', 'none'],
        ['none', 'none', 'none', 'none', 'none', 'none', 'none', 'none'],
        ['none', 'none', 'none', 'none', 'none', 'none', 'none', 'none'],
        ['wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp', 'wp'],
        ['wr', 'wn', 'wb', 'wq', 'wk', 'wb', 'wn', 'wr'],
    ]
    for i in range(8):
        for j in range(8):
            widget.drawPiece(defaultBoard[i][j], i, j)

    widget.setGeometry(0, 0, 800, 800)
    widget.show()
    app.exec_()
