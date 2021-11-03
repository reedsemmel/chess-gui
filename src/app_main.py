#!/usr/bin/env python3

# Copyright (c) 2021 Alishan Bhayani
# SPDX-License-Identifier: GPL-3.0-only

"""
File: app_main.py
Author: Alishan Bhayani
Date: 9/17/2021
Description:
    Houses the PyQt5 Application in which all components of the application will live.
"""

import sys

from ast import literal_eval
from datetime import datetime
from enum import Enum
from random import randint
from typing import Callable # pylint: disable=unused-import
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QPushButton # pylint: disable=unused-import
from PyQt5.QtWidgets import QMainWindow, QMenu, QMessageBox, QWidget
from chess import Chess

from screens import GameScreen, MainMenuScreen, SettingsScreen
from utils import Piece, Settings

class GameWindow(QMainWindow):
    """Main Window for the game that will house all the GUI elements."""
    class Game:
        """Holds all components of the game."""
        class State(Enum):
            """Denotes the states the game can be in as a whole."""
            PRE_LAUNCH = 1
            MAIN_MENU = 2
            SETTINGS = 3
            LOADING = 4
            GAME = 5
            SAVING = 6
            END_OF_GAME = 7

        def __init__(self, parent: QMainWindow) -> None:
            self.game_logic: Chess = None
            self.game_ui: QWidget = None
            self.parent: QMainWindow = parent
            self.settings: Settings = Settings()
            self.state: self.State = self.State.PRE_LAUNCH

        def close_settings(self) -> None:
            """Any actions to close the settings screen would want to run here."""
            if self.state == self.State.SETTINGS:
                self.state: self.State = self.State.LOADING
                self.game_ui: MainMenuScreen = MainMenuScreen(self.parent)
                self.state: self.State = self.State.MAIN_MENU
                self.parent.setCentralWidget(self.game_ui)

        def end(self) -> None:
            """Marks end of game and changes to end of game screen."""
            if self.state == self.State.GAME:
                self.state: self.State = self.State.LOADING
                self.state: self.State = self.State.END_OF_GAME

        def load(self) -> None:
            """Any actions to load from a previously saved game state would want to run here."""
            if self.state in (self.State.MAIN_MENU, self.State.GAME):
                self.state: self.State = self.State.LOADING
                filename: "tuple[str, str]" = QFileDialog.getOpenFileName(self.parent, "Open File")
                if filename[0] != "":
                    self.game_logic: Chess = Chess()
                    self.game_ui: GameScreen = GameScreen(self.game_logic, self.settings,
                        self.parent)
                    with open(filename[0], "rt", encoding="utf-8") as load_file:
                        self.game_ui.load(literal_eval(load_file.readline()))
                    self.state: self.State = self.State.GAME
                    self.parent.setCentralWidget(self.game_ui)
                else:
                    self.state: self.State = self.State.MAIN_MENU

        def new_game(self) -> None:
            """Any actions to start a new game would want to run here."""
            if self.state == self.State.END_OF_GAME:
                self.state: self.State = self.State.LOADING
                self.game_logic: Chess = Chess()
                self.game_ui: GameScreen = GameScreen(self.game_logic, self.settings, self.parent)
                self.state: self.State = self.State.GAME
                self.parent.setCentralWidget(self.game_ui)

        def open_settings(self) -> None:
            """Any actions to open the settings screen would want to run here."""
            if self.state == self.State.MAIN_MENU:
                self.state: self.State = self.State.LOADING
                self.game_ui: SettingsScreen = SettingsScreen(self.settings, self.parent)
                self.state: self.State = self.State.SETTINGS
                self.parent.setCentralWidget(self.game_ui)

        def play(self) -> None:
            """Starts a new game."""
            if self.state == self.State.MAIN_MENU:
                self.state: self.State = self.State.LOADING
                self.game_logic: Chess = Chess()
                self.game_ui: GameScreen = GameScreen(self.game_logic, self.settings, self.parent)
                self.state: self.State = self.State.GAME
                self.parent.setCentralWidget(self.game_ui)

        def reset(self) -> None:
            """Resets the game to the main menu."""
            if self.state == self.State.END_OF_GAME:
                self.state: self.State = self.State.LOADING
                self.game_ui: MainMenuScreen = MainMenuScreen(self.parent)
                self.state: self.State = self.State.MAIN_MENU
                self.parent.setCentralWidget(self.game_ui)

        def run(self) -> None:
            """Create the window and initializes all of the game componenets."""
            assert self.state == self.State.PRE_LAUNCH
            self.game_ui: MainMenuScreen = MainMenuScreen(self.parent)
            self.state: self.State = self.State.MAIN_MENU
            self.parent.setCentralWidget(self.game_ui)

        def save(self) -> None:
            """Any actions to preserve game state would want to run here."""
            if self.state == self.State.GAME:
                self.state: self.State = self.State.SAVING
                current_datetime_string: str = str(datetime.now()).replace(" ", "_")
                filename: "tuple[str, str]" = QFileDialog.getSaveFileName(self.parent, "Save File",
                    f"chess_game_{current_datetime_string}")
                if filename[0] != "":
                    with open(filename[0], "wt", encoding="utf-8") as save_file:
                        save_file.write(str(self.game_ui.save()))
                self.state: self.State = self.State.GAME

    def __init__(self) -> None:
        super().__init__()
        self._set_window_properties()
        self._set_menu_bar()

        self.game: GameWindow.Game = GameWindow.Game(self)

    def closeEvent(self, event: QCloseEvent) -> None: # pylint: disable=invalid-name
        """
            Ask for confirmation before closing window.
            Any auto saving would want to be triggered here.
        """
        close_confirmation: QMessageBox = QMessageBox()
        close_confirmation.setWindowTitle("Quit")
        close_confirmation.setText("Are you sure you want to quit?")
        close_confirmation.setStandardButtons(QMessageBox.Yes
            | QMessageBox.No)
        close_decision: QMessageBox.StandardButton = close_confirmation.exec()
        if close_decision == QMessageBox.Yes:
            return super().closeEvent(event)
        event.ignore()
        return None

    def close_settings_event(self) -> None:
        """Triggers the closing of the settings screens."""
        self.game.close_settings()

    def end_event(self) -> None:
        """Triggers the end of a game."""
        self.game.end()
        end_game_message: QMessageBox = QMessageBox()
        end_game_message.setWindowTitle("Game Over")
        # Should be replaced by text based on info in game logic object.
        end_game_message.setText("Placeholder")
        end_game_decisions: "dict[QPushButton, Callable]" = {}
        for button_text, func in\
            (("New Game", self.game.new_game), ("Main Menu", self.game.reset)):
            end_game_decisions[end_game_message.addButton(button_text,
                QMessageBox.ActionRole)] = func
        end_game_message.exec()
        end_game_decisions[end_game_message.clickedButton()].__call__()

    def load_event(self) -> None:
        """Triggers loading of a game."""
        self.game.load()

    def open_settings_event(self) -> None:
        """Triggers the opening of the settings screens."""
        self.game.open_settings()

    def play_event(self) -> None:
        """Triggers start of a new game."""
        self.game.play()

    def save_event(self) -> None:
        """Triggers saving of the game."""
        self.game.save()

    def show(self) -> None:
        """Shows the window and runs the setup for the game."""
        self.game.run()
        super().show()

    def _set_menu_bar(self) -> None:
        """Sets the properties of the menu bar such as File->Quit."""
        self.load_action: QAction = QAction(QIcon.fromTheme("document-open"), "Load", self)
        self.load_action.setShortcut("Ctrl+O")
        self.load_action.triggered.connect(self.load_event)

        self.quit_action: QAction = QAction(QIcon.fromTheme("application-exit"), "Quit", self)
        self.quit_action.triggered.connect(self.close)

        self.save_action: QAction = QAction(QIcon.fromTheme("document-save"), "Save", self)
        self.save_action.setShortcut("Ctrl+S")
        self.save_action.triggered.connect(self.save_event)

        self.file_menu: QMenu = self.menuBar().addMenu("File")
        self.file_menu.addAction(self.load_action)
        self.file_menu.addAction(self.save_action)
        self.file_menu.addAction(self.quit_action)

    def _set_window_properties(self) -> None:
        """Sets the properties of the window such as size and title."""
        self.setGeometry(0, 0, 853, 480)
        self.setWindowTitle("Chess")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(Piece.get_piece_pixmap(Piece(randint(1, 12)))))

    game_window: GameWindow = GameWindow()
    game_window.show()

    sys.exit(app.exec_())
