from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt6 import QtCore
from dictionnary import DICTIONNARY

# Accent selection window
class AccentWindow(QWidget):
    def __init__(self, accent_callback, vowel):
        super().__init__()
        self.accent_callback = accent_callback  # Callback function to print the selected accent
        self.vowel = vowel                      # Target vowel
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Sélection d\'Accent')
        self.setWindowFlags(QtCore.Qt.WindowType.FramelessWindowHint)
        self.layout = QVBoxLayout()
        self.label = QLabel('Appuyez sur un chiffre pour choisir un accent :')
        self.layout.addWidget(self.label)

        self.accents = DICTIONNARY[self.vowel]
        for i, accent in enumerate(self.accents):
            self.layout.addWidget(QLabel(f'{i+1}: {accent}'))

        self.setLayout(self.layout)

    # Print the accent (with the callback function, and close the selection window)
    def select_accent(self, accent):
        self.accent_callback(accent)
        print('accent callback ok')
        self.deleteLater()
        print('close OK')

    def closeEvent(self, event):
        self.accent_callback(None)
        print('accent callbacknn ok')
        event.accept()
        print('event ok')
