from PyQt6.QtCore import QObject, pyqtSignal

# Emit signal from another thread
class SignalEmitter(QObject):
    accent_signal = pyqtSignal()
