import time
import os
import threading
import select
from dictionnary import DICTIONNARY

# Try to import evdev for Wayland support
try:
    import evdev
    from evdev import InputDevice, categorize, ecodes
    EVDEV_AVAILABLE = True
except ImportError:
    EVDEV_AVAILABLE = False

# Import pynput for X11 support
try:
    from pynput import keyboard
    PYNPUT_AVAILABLE = True
except ImportError:
    PYNPUT_AVAILABLE = False

# Class to listen keyboard from another thread
class KeyboardListener:
    def __init__(self, app_manager):
        self.pressed_keys = set()       # Dictionary with all pressed key to have multi input at same time
        self.app_manager  = app_manager # Parent
        
        # Timers to manage the delay between the keys
        self.last_vowel_time = 0            # Time of the last vowel pressed
        self.vowel_delay_threshold = 0.2    # Time in second between the vowel pressing and the spacebar pressing to count a trigger
        
        # Detect display server and choose appropriate backend
        session_type = os.environ.get('XDG_SESSION_TYPE', '').lower()
        
        # Try evdev first for Wayland, then fallback to pynput for X11
        if session_type == 'wayland' and EVDEV_AVAILABLE:
            print("Detected Wayland - using evdev for keyboard capture")
            self._init_evdev()
        elif PYNPUT_AVAILABLE:
            print("Using pynput for keyboard capture")
            self._init_pynput()
        else:
            raise RuntimeError(
                "No keyboard listener available!\n"
                "For Wayland: Install evdev (pip install evdev) and ensure user is in 'input' group\n"
                "For X11: Install pynput (pip install pynput)"
            )
    
    def _init_pynput(self):
        """Initialize pynput listener (works well on X11)"""
        self.backend = 'pynput'
        self.listener = keyboard.Listener(on_press=self._on_press_pynput, on_release=self._on_release_pynput)
        self.listener.start()
    
    def _init_evdev(self):
        """Initialize evdev listener (works on Wayland)"""
        self.backend = 'evdev'
        
        # Find keyboard devices
        devices = [InputDevice(path) for path in evdev.list_devices()]
        keyboards = []
        
        for device in devices:
            # Check if device has key events (is a keyboard)
            caps = device.capabilities()
            if ecodes.EV_KEY in caps:
                # Check if it has standard letter keys
                keys = caps[ecodes.EV_KEY]
                if ecodes.KEY_A in keys and ecodes.KEY_SPACE in keys:
                    keyboards.append(device)
                    print(f"Found keyboard: {device.name} at {device.path}")
        
        if not keyboards:
            raise RuntimeError(
                "No keyboard devices found via evdev!\n"
                "Make sure your user is in the 'input' group: sudo usermod -a -G input $USER\n"
                "Then log out and log back in."
            )
        
        self.keyboards = keyboards
        
        # Start listening in background thread
        self.evdev_thread = threading.Thread(target=self._evdev_loop, daemon=True)
        self.evdev_thread.start()
    
    def _evdev_loop(self):
        """Main loop for evdev - reads from all keyboard devices"""
        # Map of device fd to device
        devices_map = {dev.fd: dev for dev in self.keyboards}
        
        while True:
            # Wait for input from any keyboard
            r, w, x = select.select(devices_map.values(), [], [])
            
            for device in r:
                try:
                    for event in device.read():
                        if event.type == ecodes.EV_KEY:
                            key_event = categorize(event)
                            if key_event.keystate in (key_event.key_down, key_event.key_hold):
                                self._on_press_evdev(event.code)
                            elif key_event.keystate == key_event.key_up:
                                self._on_release_evdev(event.code)
                except OSError:
                    # Device disconnected, remove it
                    if device.fd in devices_map:
                        del devices_map[device.fd]
                    if not devices_map:
                        print("All keyboard devices disconnected!")
                        break
    
    def _on_press_pynput(self, key):
        """Handle key press from pynput"""
        try:
            self.pressed_keys.add(key)
            self.trigger_vowel(key)
            self.trigger_accent(key)
            self.trigger_cancel()
        except AttributeError:
            pass
    
    def _on_release_pynput(self, key):
        """Handle key release from pynput"""
        if key in self.pressed_keys:
            self.pressed_keys.remove(key)
    
    def _on_press_evdev(self, keycode):
        """Handle key press from evdev"""
        # Convert evdev keycode to character
        key_char = self._evdev_keycode_to_char(keycode)
        if key_char:
            self.pressed_keys.add(keycode)
            self.trigger_vowel_evdev(key_char, keycode)
            self.trigger_accent_evdev(key_char)
            self.trigger_cancel_evdev(keycode)
    
    def _on_release_evdev(self, keycode):
        """Handle key release from evdev"""
        if keycode in self.pressed_keys:
            self.pressed_keys.remove(keycode)
    
    def _evdev_keycode_to_char(self, keycode):
        """Convert evdev keycode to character"""
        # Map common keycodes to characters
        keycode_map = {
            ecodes.KEY_A: 'a', ecodes.KEY_E: 'e', ecodes.KEY_I: 'i',
            ecodes.KEY_O: 'o', ecodes.KEY_U: 'u',
            ecodes.KEY_SPACE: ' ',
            ecodes.KEY_ESC: 'ESC',
            ecodes.KEY_1: '1', ecodes.KEY_2: '2', ecodes.KEY_3: '3',
            ecodes.KEY_4: '4', ecodes.KEY_5: '5', ecodes.KEY_6: '6',
            ecodes.KEY_7: '7', ecodes.KEY_8: '8', ecodes.KEY_9: '9',
            ecodes.KEY_0: '0',
        }
        return keycode_map.get(keycode)

    def trigger_vowel(self, key):
        """Trigger vowel detection (pynput version)"""
        # Check if a vowel is pressed
        if hasattr(key, 'char') and key.char in 'aeiou':
            self.last_vowel_time = time.time()
            self.app_manager.last_vowel = key.char

        # Check if spacebar is pressed in the good delay to count a trigger
        if key == keyboard.Key.space:
            current_time = time.time()

            if (current_time - self.last_vowel_time) >= self.vowel_delay_threshold:
                print("Espace appuyé trop lentement après la voyelle, ignorer.")
                return
            
            if self.app_manager.last_vowel:
                print("Touche voyelle + espace détectée, fenêtre ouverte !")
                self.app_manager.signal_emitter.accent_signal.emit()
    
    def trigger_vowel_evdev(self, key_char, keycode):
        """Trigger vowel detection (evdev version)"""
        # Check if a vowel is pressed
        if key_char in 'aeiou':
            self.last_vowel_time = time.time()
            self.app_manager.last_vowel = key_char

        # Check if spacebar is pressed in the good delay to count a trigger
        if keycode == ecodes.KEY_SPACE:
            current_time = time.time()

            if (current_time - self.last_vowel_time) >= self.vowel_delay_threshold:
                print("Espace appuyé trop lentement après la voyelle, ignorer.")
                return
            
            if self.app_manager.last_vowel:
                print("Touche voyelle + espace détectée, fenêtre ouverte !")
                self.app_manager.signal_emitter.accent_signal.emit()

    def trigger_accent(self, key):
        """Trigger accent selection (pynput version)"""
        if self.app_manager.accent_window_open and hasattr(key, 'char') and key.char.isdigit():
            print('Listener accent selection')
            index = int(key.char) - 1
            if 0 <= index < len(DICTIONNARY[self.app_manager.last_vowel]):
                self.app_manager.window.select_accent(self.app_manager.window.accents[index])
    
    def trigger_accent_evdev(self, key_char):
        """Trigger accent selection (evdev version)"""
        if self.app_manager.accent_window_open and key_char and key_char.isdigit():
            print('Listener accent selection')
            index = int(key_char) - 1
            if 0 <= index < len(DICTIONNARY[self.app_manager.last_vowel]):
                self.app_manager.window.select_accent(self.app_manager.window.accents[index])

    def trigger_cancel(self):
        """Trigger cancel (pynput version)"""
        if self.app_manager.accent_window_open and keyboard.Key.esc in self.pressed_keys:
            print('escape triggered')
            self.app_manager.window.deleteLater()
            print('close ok')
    
    def trigger_cancel_evdev(self, keycode):
        """Trigger cancel (evdev version)"""
        if self.app_manager.accent_window_open and keycode == ecodes.KEY_ESC:
            print('escape triggered')
            self.app_manager.window.deleteLater()
            print('close ok')
