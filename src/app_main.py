"""
File: app_main.py
Author: Alishan Bhayani
Date: 9/17/2021
Description:
    Houses the PyQt5 Application in which all components of the application will live.
"""

import sys

from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QMainWindow, QMessageBox

class GameWindow(QMainWindow):
    """Main Window for the game that will house all the GUI elements and logic processor."""
    def __init__(self):
        # Initialize QMainWindow
        super().__init__()

        # Customization
        self._set_window_properties()

    def closeEvent(self, event: QCloseEvent) -> None: # pylint: disable=invalid-name
        """Handles closing of the window by asking for confirmation."""
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

    def _set_window_properties(self):
        """Sets the properties of the window such as size, title, and menu bar."""
        self.setWindowTitle("Chess")
        self.setGeometry(0, 0, 853, 480)

        self.quit_action: QAction = QAction(QIcon.fromTheme("application-exit"), "Quit", self)
        self.quit_action.triggered.connect(self.close)

        self.menuBar().addMenu("File").addAction(self.quit_action)

if __name__ == '__main__':
    app = QApplication(sys.argv)

    gw = GameWindow()
    # gw.setCentralWidget() # Add Main Menu Here
    gw.show()

    sys.exit(app.exec_())
