from pynput import keyboard
import time
from dictionnary import DICTIONNARY
# Class to listen keyboard from another thread
class KeyboardListener:
    def __init__(self, app_manager):
        self.pressed_keys = set()       # Dictionnary with all pressed key to have multi input at same time
        self.app_manager  = app_manager # Parent
        self.listener     = keyboard.Listener(on_press=self.on_press, on_release=self.on_release)
        self.listener.start()

        # Timers to manage the delay between the keys
        self.last_vowel_time = 0            # Time of the last vowel pressed
        self.vowel_delay_threshold = 0.2    # Time in second between the vowel pressing and the spacebar pressing to count a trigger
        # TODO: check timing settings
    def on_press(self, key):
        try:
            self.pressed_keys.add(key) # Add the pressed key to the pressed_keys dict.
            self.trigger_vowel(key)    # Trigger the vowel target
            self.trigger_accent(key)   # Trigger the accent asked
            self.trigger_cancel()      # Trigger the cancel
        except AttributeError:
            pass

    def on_release(self, key):
        if key in self.pressed_keys:
            self.pressed_keys.remove(key) # Remove released key from the pressed_key dict

    def trigger_vowel(self, key):
        # Vérifie si une voyelle est pressée
        if hasattr(key, 'char') and key.char in 'aeiou':
            self.last_vowel_time = time.time()  # Save the timestamp of the last vowel
            self.app_manager.last_vowel = key.char

        # Check if a spacebar is pressed in the good delay to count a trigger
        if key == keyboard.Key.space:
            current_time = time.time()

            if (current_time - self.last_vowel_time) >= self.vowel_delay_threshold:
                print("Espace appuyé trop rapidement après la voyelle, ignorer.")
                return
            
            if self.app_manager.last_vowel:
                print("Touche voyelle + espace détectée, fenêtre ouverte !")

                # Émettre un signal pour ouvrir la fenêtre dans le thread principal
                self.app_manager.signal_emitter.accent_signal.emit()

    def trigger_accent(self, key):
        if self.app_manager.accent_window_open and hasattr(key, 'char') and key.char.isdigit():
            print('Listener accent selection')
            index = int(key.char) - 1
            if 0 <= index < len(DICTIONNARY[self.app_manager.last_vowel]):  # index set manually for test purposes (TODO: replace)
                self.app_manager.window.select_accent(self.app_manager.window.accents[index])

    def trigger_cancel(self):
        if self.app_manager.accent_window_open and keyboard.Key.esc in self.pressed_keys:
            print('escape triggered')
            self.app_manager.window.deleteLater()
            print('close ok')
