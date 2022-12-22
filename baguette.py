from pynput import keyboard
from baguette_ui import BaguetteUi
import time
import pyautogui


class Baguette:

    def __init__(self):
        self.time = None
        self.choice = 'DEFAULT'

    def on_key_release(self, key):  # what to do on key-release
        time_taken = round(time.time() - self.time, 2)  # rounding the long decimal float
        print("[TARGET] The key", key, " is pressed for", time_taken, 'seconds')
        if time_taken > 1:
            pyautogui.write(self.choice)
            BaguetteUi(key, self).generate_window()
        return False  # stop detecting more key-releases

    @staticmethod
    # todo: make it lambda
    def on_key_press(key):
        return False  # stop detecting more key-presses

    def key_handler(self):
        while True:
            with keyboard.Listener(
                    on_press=self.on_key_press) as press_listener:  # setting code for listening key-press
                press_listener.join()

            self.time = time.time()  # reading time in sec

            with keyboard.Listener(
                    on_release=self.on_key_release) as release_listener:  # setting code for listening key-release
                release_listener.join()

    def set_choice(self, choice):
        self.choice = choice
