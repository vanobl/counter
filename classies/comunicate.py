from PySide2.QtCore import QObject, Signal


class Communicate(QObject):
    speak_word = Signal(str)
