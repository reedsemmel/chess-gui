# Copyright (c) 2021 Alishan Bhayani
# SPDX-License-Identifier: GPL-3.0-only

"""
File: screens.py
Author: Alishan Bhayani
Date: 9/27/2021
Description:
    Houses the the different screen states for the application.
"""

from typing import Callable, Optional
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QResizeEvent
from PyQt5.QtWidgets import QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from chess import Chess

from interactive_board import InteractiveBoard
from utils import Piece, Player, Settings

def make_button(content: str, func: Callable, parent: Optional['QWidget'] = None) -> QPushButton:
    """Returns a button with the specified content and function."""
    button: QPushButton = QPushButton(content, parent)
    button.clicked.connect(func)
    return button

class MainMenuScreen(QWidget):
    """Screen that houses main menu elements like the title, play button, etc."""
    def __init__(self, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self._set_layout()
        self._add_elements()

    def _add_buttons(self) -> None:
        """Adds various buttons to the layout."""
        buttons: QVBoxLayout = QVBoxLayout()
        buttons.addWidget(make_button("Play", self.parent().play_event, self))
        buttons.addWidget(make_button("Load", self.parent().load_event, self))
        buttons.addWidget(make_button("Settings", self.parent().open_settings_event, self))
        buttons.addWidget(make_button("Quit", self.parent().close, self))
        self.layout.addLayout(buttons, 1, 0, Qt.AlignHCenter | Qt.AlignTop)

    def _add_elements(self) -> None:
        """Adds all the elements unique to this screen to the layout."""
        assert isinstance(self.layout, QGridLayout)
        self._add_title()
        self._add_buttons()

    def _add_title(self) -> None:
        """Adds title to the layout."""
        self.layout.addWidget(QLabel("<h1>CHESS</h1>"), 0, 0, Qt.AlignTop | Qt.AlignHCenter)

    def _set_layout(self) -> None:
        """Sets the widget's layout."""
        self.layout: QGridLayout = QGridLayout(self)
        self.setLayout(self.layout)

class GameScreen(QWidget):
    """Screen that houses the actual game elements like the chessboard and other features."""
    class CenteredSquareContainer(QWidget):
        """Widget wrapper that keeps its child widget square and centered on both axes."""
        def __init__(self, child: QWidget, parent: QWidget):
            super().__init__(parent)
            self._set_layout()
            self._set_widget_properties()
            self.layout.addWidget(child)

        def resizeEvent(self, a0: QResizeEvent) -> None: # pylint: disable=invalid-name
            """Controls resizing to ensure the child widget stays centered and square."""
            height, width = a0.size().height(), a0.size().width()
            if width > height:
                margin = round((width - height) / 2)
                self.setContentsMargins(margin, 0, margin, 0)
            else:
                margin = round((height - width) / 2)
                self.setContentsMargins(0, margin, 0, margin)

        def _set_layout(self) -> None:
            """Sets the widget's layout."""
            self.layout: QHBoxLayout = QHBoxLayout(self)
            self.setLayout(self.layout)

        def _set_widget_properties(self) -> None:
            """Sets the widgets's properties."""
            self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

    class CapturedPiecesBar(QFrame):
        """
            Widget that creates a bar to display captured pieces
            as an indicator of the state of the game.
        """
        def __init__(self, parent: QWidget) -> None:
            super().__init__(parent)
            self._set_custom_properties()
            self._set_layout()
            self._set_widget_properties()

        def add_piece(self, piece: Piece) -> None:
            """Adds a piece to the layout."""
            self.pieces.append(piece)
            piece_image: QLabel = QLabel(self)
            piece_image.setPixmap(Piece.get_piece_pixmap(piece))
            piece_image.setScaledContents(True)
            self.layout.addWidget(piece_image)

        def export_pieces(self) -> "tuple[int]":
            """Returns tuple of current pieces in the bar."""
            return tuple(int(piece) for piece in self.pieces)

        def import_pieces(self, pieces: "tuple[int]") -> None:
            """Sets the current pieces in the bar."""
            for piece in pieces:
                self.add_piece(Piece(piece))

        def resizeEvent(self, a0: QResizeEvent) -> None: # pylint: disable=invalid-name
            """Controls resizing to ensure the child widgets in the layout stay square."""
            self.setMaximumWidth(a0.size().height() * (len(self.pieces) + 1))
            super().resize(a0.size().height() * len(self.pieces), a0.size().height())

        def _set_custom_properties(self) -> None:
            """Sets properties unique to this widget."""
            self.pieces: "list[Piece]" = []

        def _set_layout(self) -> None:
            """Sets the widget's layout."""
            self.layout: QHBoxLayout = QHBoxLayout(self)
            self.layout.setContentsMargins(0, 0, 0, 0)
            self.layout.setSpacing(0)
            self.setLayout(self.layout)

        def _set_widget_properties(self) -> None:
            """Sets the widgets's properties."""
            self.setFixedHeight(50)
            self.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
            self.setLineWidth(3)
            self.setStyleSheet("background-color: #f5f5dc;")

    def __init__(self, settings: Settings, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self._set_custom_properties(settings)
        self._set_layout()
        self._add_elements()

    def capture_piece(self, piece: Piece, player: Player) -> None:
        """Adds captured piece to specified player's captured bar."""
        self.players[player].add_piece(piece)

    def load(self, states: "tuple[tuple[int, tuple[int]], tuple[int, tuple[int]]]") -> None: # pylint: disable=line-too-long
        """Any actions to restore previously preserved game would want to run here."""
        for (player, pieces) in states:
            self.players[Player(player)].import_pieces(pieces)

    def save(self)-> "tuple[tuple[int, tuple[int]], tuple[int, tuple[int]]]":
        """Any actions to preserve the game state would want to run here."""
        return ((int(Player.P1), self.players[Player.P1].export_pieces()),
            (int(Player.P2), self.players[Player.P2].export_pieces()))

    # def test_capture(self) -> None:
    #     self.capture_piece(Piece.WB, Player.P1)
    #     self.capture_piece(Piece.BB, Player.P2)

    def _add_board(self) -> None:
        """Adds the board to the layout."""
        self.layout.addWidget(self.CenteredSquareContainer(self.board, self), 1, 0)
        self.layout.setRowStretch(1, 8)

    def _add_elements(self):
        """Adds all the elements unique to this screen to the layout."""
        assert isinstance(self.layout, QGridLayout)
        self._add_enemy_side()
        self._add_board()
        self._add_player_side()

    def _add_enemy_side(self) -> None:
        """Adds the enemy side's layout to the layout."""
        enemy_layout: QHBoxLayout = QHBoxLayout()
        enemy_layout.addWidget(self.players[Player.P2], 0, Qt.AlignLeft | Qt.AlignVCenter)
        enemy_layout.addWidget(QLabel(self.settings.opponent_name), 1, Qt.AlignRight
            | Qt.AlignVCenter)
        self.layout.addLayout(enemy_layout, 0, 0, Qt.AlignTop)
        self.layout.setRowStretch(0, 1)

    def _add_player_side(self) -> None:
        """Adds the player side's layout to the layout."""
        player_layout: QHBoxLayout = QHBoxLayout()
        player_layout.addWidget(QLabel(self.settings.player_name), 1, Qt.AlignLeft
            | Qt.AlignVCenter)
        player_layout.addWidget(self.players[Player.P1], 0, Qt.AlignRight | Qt.AlignVCenter)
        player_layout.addWidget(make_button("End Game", self.parent().end_event, self))
        # player_layout.addWidget(make_button("Test", self.test_capture, self))
        self.layout.addLayout(player_layout, 2, 0, Qt.AlignBottom)
        self.layout.setRowStretch(2, 1)

    def _set_custom_properties(self, settings: Settings) -> None:
        """Sets properties unique to this widget."""
        self.chess: Chess = Chess()
        self.board: InteractiveBoard = InteractiveBoard(self.chess, settings)
        self.players: "dict[Player, self.CapturedPiecesBar]" = {
            Player.P1: self.CapturedPiecesBar(self),
            Player.P2: self.CapturedPiecesBar(self)
        }
        self.settings: Settings = settings

    def _set_layout(self) -> None:
        """Sets the widget's layout."""
        self.layout: QGridLayout = QGridLayout(self)
        self.setLayout(self.layout)

class EndGameScreen(QWidget):
    """Screen that houses the end of game elements like the winner and other features."""
    def __init__(self, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self._set_layout()
        self._add_elements()

    def _add_elements(self) -> None:
        """Adds all elements unique to this screen to the layout."""
        assert isinstance(self.layout, QGridLayout)
        self._add_placeholder()

    def _add_placeholder(self) -> None:
        """Adds placeholder text to the layout."""
        self.layout.addWidget(QLabel("This is the end of game screen.", self), 0, 0,
            Qt.AlignCenter)

    def _set_layout(self) -> None:
        """Sets the widget's layout."""
        self.layout: QGridLayout = QGridLayout(self)
        self.setLayout(self.layout)

class SettingsScreen(QWidget):
    """Screen that houses elements that allow user to change allowed settings."""
    def __init__(self, settings: Settings, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)
        self._set_custom_properties(settings)
        self._set_layout()
        self._add_elements()

    def _add_elements(self) -> None:
        """Adds all elements unique to this screen to the layout."""
        self._add_back_button()
        self._add_player_name_form()
        self._add_colors_hex_form()

    def _add_back_button(self) -> None:
        """Adds a back button to the layout for returning to main menu."""
        back_button: QPushButton = make_button("Back", self.parent().close_settings_event, self)
        self.layout.addWidget(back_button)
        self.setFocusProxy(back_button)

    def _add_colors_hex_form(self) -> None:
        """Add form to change the colors of the alternating tiles."""
        hex_regex: str = "^#([A-Fa-f0-9]{3}|[A-Fa-f0-9]{6})$"

        self.primary_tile_color_form_field.setMaxLength(7)
        self.primary_tile_color_form_field.setValidator(QRegExpValidator(
            QRegExp(hex_regex), self))
        self.primary_tile_color_form_field.editingFinished.connect(
            self._handle_primary_color_change)
        self.primary_tile_color_form_field.returnPressed.connect(
            self._handle_primary_color_change)
        self.layout.addRow("Primary Tile Color: ", self.primary_tile_color_form_field)

        self.secondary_tile_color_form_field.setMaxLength(7)
        self.secondary_tile_color_form_field.setValidator(QRegExpValidator(
            QRegExp(hex_regex), self))
        self.secondary_tile_color_form_field.editingFinished.connect(
            self._handle_secondary_color_change)
        self.secondary_tile_color_form_field.returnPressed.connect(
            self._handle_secondary_color_change)
        self.layout.addRow("Secondary Tile Color: ", self.secondary_tile_color_form_field)

    def _add_player_name_form(self) -> None:
        """Add form to change player name to the layout."""
        self.player_name_form_field.setMaxLength(20)
        self.player_name_form_field.setValidator(QRegExpValidator(
            QRegExp("([A-Za-z]|[0-9]|[ ])+"), self))
        self.player_name_form_field.editingFinished.connect(self._handle_name_change)
        self.player_name_form_field.returnPressed.connect(self._handle_name_change)
        self.layout.addRow("Player Name:", self.player_name_form_field)

    def _handle_name_change(self) -> None:
        """Reflects change in form field to the player name stored in settings."""
        self.settings.change_name(self.player_name_form_field.text(), False)

    def _handle_primary_color_change(self) -> None:
        """Reflects change in form field to the primary hex color stored in settings."""
        self.settings.change_primary_color(self.primary_tile_color_form_field.text(), False)

    def _handle_secondary_color_change(self) -> None:
        """Reflects change in form field to the secondary hex color stored in settings."""
        self.settings.change_secondary_color(self.secondary_tile_color_form_field.text(), False)

    def _set_custom_properties(self, settings: Settings) -> None:
        """Sets properties unique to this widget."""
        self.settings: Settings = settings
        self.player_name_form_field: QLineEdit = QLineEdit(self.settings.player_name, self)
        self.primary_tile_color_form_field: QLineEdit = QLineEdit(self.settings.primary_color,
            self)
        self.secondary_tile_color_form_field: QLineEdit = QLineEdit(self.settings.secondary_color,
            self)

    def _set_layout(self) -> None:
        """Sets the widget's layout."""
        self.layout: QFormLayout = QFormLayout(self)
        self.setLayout(self.layout)
