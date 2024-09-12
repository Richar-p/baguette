from accent_window import AccentWindow
from PyQt6.QtWidgets import QApplication
from signal_emitter import SignalEmitter
from pynput import keyboard
import sys
import time

# UI Launching and unicity gestion
class AppManager:
    def __init__(self):
        
        self.app                = QApplication(sys.argv)    # Application itself
        self.window             = None                      # Contain an AccentWindow class when it is openned
        self.accent_window_open = False                     # Boolean who send signal to open/close AccentWindow
        self.last_vowel         = None                      # Variable used to store the vowel to replace
        self.signal_emitter     = SignalEmitter()           # SignalEmitter class used to communicate between KeyboardListener thread and the window thread
        self.signal_emitter.accent_signal.connect(self.open_accent_window)  # Connecter le signal au slot

    # Method to launch the window
    def open_accent_window(self):
        # Return and do nothing if the window is already open
        if self.accent_window_open:
            return

        # Create a new window if there is no one openned
        self.window = AccentWindow(self.insert_accent, self.last_vowel)
        self.window.show()
        self.accent_window_open = True

    # Method to insert an accent when triggers are on
    # This method are passed as "accent_callback" into the AccentWindow class
    def insert_accent(self, accent):
        if accent is not None and self.last_vowel:
            # Simulate keyboard to press 3 times backspace.
            # 1 for the focus, 2 for the space, 3 for the vowel
            # Time sleep are added to simulate human pression
            # TODO: delete the sleep to check if it can work without
            for i in range(3):
                keyboard.Controller().press(keyboard.Key.backspace)
                keyboard.Controller().release(keyboard.Key.backspace)

            # Type the selected accent
            keyboard.Controller().type(accent)

            # Logs
            print(f"Accent '{accent}' inséré à la place de '{self.last_vowel}'")

            # Reset the last vowel
            self.last_vowel = None

        # Close the window (by the signal)
        self.accent_window_open = False
        
    def run(self):
        # The PyQT app are not stopping when there is no windows openned
        self.app.setQuitOnLastWindowClosed(False)
        self.app.exec()
