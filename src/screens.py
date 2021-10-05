"""
File: screens.py
Author: Alishan Bhayani
Date: 9/27/2021
Description:
    Houses the the different screen states for the application.
"""

from typing import Callable, Optional, Union
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QGridLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from interactive_board import InteractiveBoard

def make_button(content: str, func: Callable, parent: Union[QWidget, None] = None) -> QPushButton:
    """Returns a button with the specified content and function."""
    button: QPushButton = QPushButton(content, parent)
    button.clicked.connect(func)
    return button

class MainMenuScreen(QWidget):
    """Screen that houses main menu elements like the title, play button, etc."""
    def __init__(self, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.setLayout(QGridLayout(self))
        self._add_elements()

    def _add_elements(self):
        """Adds all the elements unique to this screen to the layout."""
        assert isinstance(self.layout(), QGridLayout)

        # Title
        self.layout().addWidget(QLabel("<h1>CHESS</h1>"), 0, 0, Qt.AlignTop | Qt.AlignHCenter)

        # Buttons
        buttons: QVBoxLayout = QVBoxLayout()

        buttons.addWidget(make_button("Play", self.parent().play_event, self))
        buttons.addWidget(make_button("Load", self.parent().load_event, self))
        buttons.addWidget(make_button("Quit", self.parent().close, self))

        self.layout().addLayout(buttons, 1, 0, Qt.AlignHCenter | Qt.AlignTop)

class GameScreen(QWidget):
    """Screen that houses the actual game elements like the chessboard and other features."""
    class CenteredSquareContainer(QWidget):
        """Widget wrapper that keeps its child widget square and centered on both axes."""
        def __init__(self, child: QWidget, parent: QWidget):
            super().__init__(parent)
            self.setLayout(QHBoxLayout(self))
            self.layout().addWidget(child)

        def resizeEvent(self, a0: QResizeEvent) -> None: # pylint: disable=invalid-name
            """Controls resizing to ensure the child widget stays centered and square."""
            height, width = a0.size().height(), a0.size().width()
            if width > height:
                margin = round((width - height) / 2)
                self.setContentsMargins(margin, 0, margin, 0)
            else:
                margin = round((height - width) / 2)
                self.setContentsMargins(0, margin, 0, margin)

    def __init__(self, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.setLayout(QGridLayout(self))
        self._add_elements()

    def _add_elements(self):
        """Adds all the elements unique to this screen to the layout."""
        assert isinstance(self.layout(), QGridLayout)

        # Title
        self.layout().addWidget(QLabel("This is the game screen.", self), 0, 0, Qt.AlignTop
            | Qt.AlignHCenter)

        # Board
        self.layout().addWidget(self.CenteredSquareContainer(InteractiveBoard(), self), 1, 0, 8, 1)

        # Temporary End Game Button
        self.layout().addWidget(make_button("End Game", self.parent().end_event, self), 9, 0,
            Qt.AlignBottom | Qt.AlignHCenter)

class EndGameScreen(QWidget):
    """Screen that houses the end of game elements like the winner and other features."""
    def __init__(self, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self.setLayout(QGridLayout(self))
        self.layout().addWidget(QLabel("This is the end of game screen.", self), 0, 0, Qt.AlignCenter)
