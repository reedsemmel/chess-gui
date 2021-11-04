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
from PyQt5.QtCore import QRegExp, QSize, Qt
from PyQt5.QtGui import QFont, QRegExpValidator, QResizeEvent
from PyQt5.QtWidgets import QFormLayout, QGridLayout, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from chess import Chess

from interactive_board import InteractiveBoard
from utils import Settings

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

            # Set Layout
            self.layout: QHBoxLayout = QHBoxLayout(self)

            # Set Size Policy
            self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)

            # Add Child
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

    def __init__(self, chess: Chess, settings: Settings, parent: Optional['QWidget'] = None) -> None: # pylint: disable=line-too-long
        super().__init__(parent)

        # Add Instance Variables
        self.board: InteractiveBoard = InteractiveBoard(chess, settings)
        self.original_size: QSize = None
        self.resizables: tuple = ()

        # Set Layout
        self.layout: QGridLayout = QGridLayout(self)

        # Back Button
        back_button: QPushButton = make_button("Back", self.parent().abandon_game_event, self)
        back_button.setStyleSheet("padding: 3px 24px;")
        self.layout.addWidget(back_button, 0, 0, 2, 1, Qt.AlignTop | Qt.AlignLeft)

        # Add Board
        board: GameScreen.CenteredSquareContainer = self.CenteredSquareContainer(self.board, self)
        board.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(board, 0, 1, 2, 1)
        self.layout.setColumnStretch(1, 1)

        # Add Player Names
        opponent_name: QLabel = QLabel(settings.opponent_name)
        opponent_name.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(opponent_name, 0, 2, Qt.AlignTop | Qt.AlignHCenter)
        player_name: QLabel = QLabel(settings.player_name)
        player_name.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(player_name, 1, 2, Qt.AlignBottom | Qt.AlignHCenter)

        # Configure Resizable Elements
        self.resizables = (back_button, opponent_name, player_name)

    def resizeEvent(self, a0: QResizeEvent) -> None: # pylint: disable=invalid-name
        """Controls resizing to scale text."""
        if self.original_size is None:
            self.original_size: QSize = a0.size()
        ratios: tuple = (a0.size().height() / self.original_size.height(),
            a0.size().width() / self.original_size.width())
        scale: float = max(ratios) if any(ratio < 1 for ratio in ratios) else min(ratios)
        if scale > 0:
            size: int = max(9, round(scale * 9))
            font: QFont = QFont("Sans Serif", size)
            for widget in self.resizables:
                widget.setFont(font)
        return super().resizeEvent(a0)

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
