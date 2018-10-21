import os

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget
from PySide2.QtCore import QFile

# создадим сессию
conn = Connect().get_session()

over = Communicate()


class EditService(QWidget):
    def __init__(self, action, parent=None):
        super(EditService, self).__init__(parent)
        self.path = os.path.join('faces', 'edit_service.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        self.action = action

        # определим элементы управления
        self.btn_action = self.dialog.findChild(QPushButton, 'btn_action')
        self.btn_exit = self.dialog.findChild(QPushButton, 'btn_exit')
        self.edit_name = self.dialog.findChild(QLineEdit, 'edit_name')
