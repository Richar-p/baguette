from keyboard_listener import KeyboardListener
from app_manager import AppManager
import threading

if __name__ == '__main__':
    # # Run PyQt on main thread (or it cannot run)
    app_manager = AppManager()

    # # Run the keyboard listener in another thread
    listener_thread = threading.Thread(target=lambda: KeyboardListener(app_manager))
    listener_thread.daemon = True
    listener_thread.start()

    app_manager.run()
    # print(list(DICTIONNARY.keys()))
