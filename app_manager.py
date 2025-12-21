from accent_window import AccentWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import QTimer
from signal_emitter import SignalEmitter
from pynput import keyboard
import sys
import time
try:
    from Xlib import display, X
    from Xlib.error import BadWindow
    XLIB_AVAILABLE = True
except ImportError:
    XLIB_AVAILABLE = False

# UI Launching and unicity gestion
class AppManager:
    # Focus restoration delay in milliseconds
    # This allows Qt event loop to process window show before restoring focus
    FOCUS_RESTORE_DELAY_MS = 50
    
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

        # Save the currently focused window before showing our window
        saved_window = None
        d = None
        if XLIB_AVAILABLE:
            try:
                d = display.Display()
                saved_window = d.get_input_focus().focus
            except Exception as e:
                print(f"Warning: Could not get focused window: {e}")
                d = None  # Clear display if we had an error

        # Create a new window if there is no one openned
        self.window = AccentWindow(self.insert_accent, self.last_vowel)
        self.window.show()
        self.accent_window_open = True

        # Restore focus to the previously active window after a short delay
        # This allows Qt to fully process the window show event first
        if XLIB_AVAILABLE and saved_window and d:
            def restore_focus():
                # Validate captured variables are still valid
                if saved_window is None or d is None:
                    return
                try:
                    saved_window.set_input_focus(X.RevertToParent, X.CurrentTime)
                    d.flush()
                except Exception as e:
                    print(f"Warning: Could not restore focus: {e}")
            
            # Use QTimer to delay focus restoration
            # This allows the Qt event loop to process the window show event
            QTimer.singleShot(self.FOCUS_RESTORE_DELAY_MS, restore_focus)

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
            print(f"Accent '{accent}' replaced '{self.last_vowel}'")

            # Reset the last vowel
            self.last_vowel = None

        # Close the window (by the signal)
        self.accent_window_open = False
        
    def run(self):
        # The PyQT app are not stopping when there is no windows openned
        self.app.setQuitOnLastWindowClosed(False)
        
        # Set up a timer to allow Python signal handlers to run
        # This enables CTRL+C to work properly
        timer = QTimer()
        timer.timeout.connect(lambda: None)  # Just let Python process signals
        timer.start(100)  # Check every 100ms
        
        self.app.exec()
