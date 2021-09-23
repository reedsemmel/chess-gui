"""
File: app_main.py
Author: Alishan Bhayani
Date: 9/17/2021
Description:
    Houses the PyQt5 Application in which all components of the application will live.
"""

import sys

from enum import Enum
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QMenu, QMessageBox

class GameWindow(QMainWindow):
    """Main Window for the game that will house all the GUI elements."""
    class Game:
        """Holds all components of the game."""
        class State(Enum):
            """Denotes the states the game can be in as a whole."""
            PRE_LAUNCH = 1
            MAIN_MENU = 2
            LOADING = 3
            GAME = 4
            SAVING = 5
            END_OF_GAME = 6

        def __init__(self) -> None:
            self.game_logic = None
            self.game_ui = None
            self.state: self.State = self.State.PRE_LAUNCH

        def load(self) -> None:
            """Any actions to load from a previously saved game state would want to run here."""
            if self.state in (self.State.MAIN_MENU, self.State.GAME):
                self.state = self.State.LOADING
                # Do loading stuff
                self.state = self.State.GAME

        def run(self) -> None:
            """Create the window and initializes all of the game componenets."""
            assert self.state == self.State.PRE_LAUNCH
            # Do pre launch stuff
            self.state = self.State.MAIN_MENU

        def save(self) -> None:
            """Any actions to preserve game state would want to run here."""
            if self.state == self.State.GAME:
                self.state = self.State.SAVING
                # Do saving stuff
                self.state = self.State.GAME

    def __init__(self) -> None:
        super().__init__()
        self._set_window_properties()
        self._set_menu_bar()

        self.game: GameWindow.Game = GameWindow.Game()

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
            self.save_event()
            return super().closeEvent(event)
        event.ignore()
        return None

    def load_event(self) -> None:
        """Triggers loading of a game."""
        self.game.load()

    def save_event(self) -> None:
        """Triggers saving of the game."""
        self.game.save()

    def show(self) -> None:
        """Shows the window and runs the setup for the game."""
        self.game.run()
        # self.setCentralWidget() # Assign to Main Menu here
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

    game_window: GameWindow = GameWindow()
    game_window.show()

    sys.exit(app.exec_())
