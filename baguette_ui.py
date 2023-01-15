from tkinter import *
import keyboard


class BaguetteUi:

    def __init__(self, key, baguette):
        self.root = Tk()
        self.root.geometry("100x40")
        # todo: fix the callback problem with the no-border window
        # self.root.overrideredirect(1)
        self.baguette = baguette
        self.key = key
        self.canvas_value = None
        self.canvas_keys = None

    @staticmethod
    # todo: real data
    def fill_instructions(self):
        self.canvas_value.create_text(50, 10, text="HELLO", fill="black", font=('Helvetica 10 bold'))
        self.canvas_value.pack()

    def on_key_press(self, key):
        print("[CHOICE] The key", key.char, " is pressed")
        self.baguette.set_choice(key.char)
        self.root.destroy()

    def generate_window(self):
        self.canvas_value = Canvas(self.root, width=100, height=100, bg="SpringGreen2")
        self.fill_instructions(self)
        keyboard.add_hotkey('a', self.on_key_press, args=('a',))
        self.root.mainloop()
