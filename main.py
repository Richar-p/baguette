from keyboard_listener import KeyboardListener
from app_manager import AppManager
import threading
import signal
import sys

def signal_handler(sig, frame):
    """Handle CTRL+C gracefully"""
    print("\nShutting down baguette...")
    sys.exit(0)

if __name__ == '__main__':
    # Set up signal handler for CTRL+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # # Run PyQt on main thread (or it cannot run)
    app_manager = AppManager()

    # # Run the keyboard listener in another thread
    listener_thread = threading.Thread(target=lambda: KeyboardListener(app_manager))
    listener_thread.daemon = True
    listener_thread.start()

    app_manager.run()
    # print(list(DICTIONNARY.keys()))
