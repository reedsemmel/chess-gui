# Copyright (c) 2021 Alishan Bhayani
# SPDX-License-Identifier: GPL-3.0-only

"""
File: screens.py
Author: Alishan Bhayani
Date: 9/27/2021
Description:
    Houses the the different screen states for the application.
"""

from typing import Any, Callable, Dict, Optional, Tuple
from PyQt5.QtCore import QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator, QResizeEvent
from PyQt5.QtWidgets import QFormLayout, QGridLayout, QHBoxLayout, QLabel
from PyQt5.QtWidgets import QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QWidget
from chess import Chess

from interactive_board import InteractiveBoard
from utils import Settings

def make_button(content: str, func: Callable, parent: Optional[QWidget] = None) -> QPushButton:
    """Returns a button with the specified content and function."""
    button: QPushButton = QPushButton(content, parent)
    button.clicked.connect(func)
    button.setObjectName("resizable")
    return button

class Screen(QWidget):
    """Screen that allows for resizing text and button text."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Initialize Instance Variables
        self.current_font_size: int = Settings.DEFAULT_FONT_SIZE

        # Set Style
        self._set_style_sheet()

    def resizeEvent(self, a0: QResizeEvent) -> None: # pylint: disable=invalid-name
        """Controls resizing to scale text."""
        ratios: Tuple[float, float] = (
            a0.size().height() / Settings.DEFAULT_WINDOW_SIZE.height(),
            a0.size().width() / Settings.DEFAULT_WINDOW_SIZE.width())
        scale: float = max(ratios) if any(ratio < 1 for ratio in ratios) else min(ratios)
        if scale > 0:
            size: int = max(Settings.DEFAULT_FONT_SIZE, round(scale * Settings.DEFAULT_FONT_SIZE))
            self._set_style_sheet(size)
        return super().resizeEvent(a0)

    def _set_style_sheet(self, size: int = Settings.DEFAULT_FONT_SIZE) -> None:
        """Sets the style sheet for the widget."""
        style: str = f"""
            QWidget {{ font-size: {size}px; }}
            QPushButton#resizable {{ padding: 3px 24px; }}
        """
        if self.current_font_size != size:
            self.setStyleSheet(style)
            self.current_font_size: int = size

class MainMenuScreen(Screen):
    """Screen that houses main menu elements like the title, play button, etc."""
    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Set Layout
        self.layout: QGridLayout = QGridLayout(self)

        # Add Title
        self.layout.addWidget(QLabel("<h1>CHESS</h1>"), 0, 0, Qt.AlignTop | Qt.AlignHCenter)

        # Add Buttons
        buttons: QVBoxLayout = QVBoxLayout()
        for name, func in (("Play", self.parent().play_event), ("Load", self.parent().load_event),
            ("Settings", self.parent().open_settings_event), ("Quit", self.parent().close)):
            buttons.addWidget(make_button(name, func, self))
        self.layout.addLayout(buttons, 1, 0, Qt.AlignHCenter | Qt.AlignTop)

class GameScreen(Screen):
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
                margin: int = round((width - height) / 2)
                self.setContentsMargins(margin, 0, margin, 0)
            else:
                margin: int = round((height - width) / 2)
                self.setContentsMargins(0, margin, 0, margin)

    def __init__(self, chess: Chess, settings: Settings, parent: Optional[QWidget] = None) -> None: # pylint: disable=line-too-long
        super().__init__(parent)

        # Initialize Instance Variables
        self.board: InteractiveBoard = InteractiveBoard(chess, settings, parent)
        self.initial_layout: bool = True

        # Set Layout
        self.layout: QGridLayout = QGridLayout(self)

        # Add Back Button
        back_button: QPushButton = make_button("Back", self.parent().abandon_game_event, self)
        self.layout.addWidget(back_button, 0, 0, 2, 1, Qt.AlignTop | Qt.AlignLeft)

        # Add Board
        board: GameScreen.CenteredSquareContainer = self.CenteredSquareContainer(self.board, self)
        board.setContentsMargins(10, 10, 10, 10)
        self.layout.addWidget(board, 0, 1, 2, 1)
        self.layout.setColumnStretch(1, 1)

        # Add Player Names
        self.opponent_name: QLabel = QLabel(settings.opponent_name)
        self.opponent_name.setContentsMargins(0, 10, 10, 10)
        self.layout.addWidget(self.opponent_name, 0, 2, Qt.AlignTop | Qt.AlignHCenter)
        self.player_name: QLabel = QLabel(settings.player_name)
        self.player_name.setContentsMargins(0, 10, 10, 10)
        self.layout.addWidget(self.player_name, 1, 2, Qt.AlignBottom | Qt.AlignHCenter)

    def swap_board(self) -> None:
        """Updates the board."""
        self.board.swap_view_side()
        self.layout.addWidget(self.player_name if self.initial_layout else self.opponent_name, 0, 2, Qt.AlignTop | Qt.AlignHCenter)
        self.layout.addWidget(self.opponent_name if self.initial_layout else self.player_name, 1, 2, Qt.AlignBottom | Qt.AlignHCenter)
        self.initial_layout: bool = not self.initial_layout

class SettingsScreen(Screen):
    """Screen that houses elements that allow user to change allowed settings."""

    def __init__(self, settings: Settings, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        # Set Layout
        self.layout: QVBoxLayout = QVBoxLayout(self)

        # Add Back Button
        back_button: QPushButton = make_button("Back", self.parent().close_settings_event, self)
        self.layout.addWidget(back_button, 0, Qt.AlignTop | Qt.AlignLeft)
        self.setFocusProxy(back_button)

        # Add Form for Configurable Settings
        settings_form: QFormLayout = QFormLayout()
        settings_form.setContentsMargins(10, 10, 10, 10)
        for configurable in settings.configurables:
            configurable: Dict[str, Any] = settings.configurables[configurable]
            line_edit: QLineEdit = QLineEdit(configurable["value"], self)
            line_edit.setMaxLength(configurable["max_length"])
            line_edit.setValidator(QRegExpValidator(QRegExp(configurable["regex"]), line_edit))
            edit_func = lambda configurable=configurable, line_edit=line_edit:\
                self._handle_change(configurable["handle_func"], line_edit)
            line_edit.editingFinished.connect(edit_func)
            line_edit.returnPressed.connect(edit_func)
            settings_form.addRow(configurable["form_header"], line_edit)
        self.layout.addLayout(settings_form, 1)

    @staticmethod
    def _handle_change(func: Callable[[str, bool], None], line_edit: QLineEdit) -> None:
        """Handles changes to the settings form."""
        func(line_edit.text(), False)
