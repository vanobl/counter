import os

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QLabel, QWidget
from PySide2.QtCore import QFile
# from PySide2 import QtGui

# импортируем таблицы
# from db.alchemy import Company
# создадим сессию
conn = Connect().get_session()

over = Communicate()


class EditCompany(QWidget):
    def __init__(self, action, parent=None):
        super(EditCompany, self).__init__(parent)
        self.path = os.path.join('faces', 'edit_company.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        self.action = action

        # определим элементы управления
        self.btn_action = self.dialog.findChild(QPushButton, 'btn_action')
        self.btn_exit = self.dialog.findChild(QPushButton, 'btn_exit')
        self.edit_company = self.dialog.findChild(QLineEdit, 'edit_company')
        self.edit_inn = self.dialog.findChild(QLineEdit, 'edit_inn')
        self.edit_ogrn = self.dialog.findChild(QLineEdit, 'edit_ogrn')
        self.edit_address = self.dialog.findChild(QLineEdit, 'edit_address')
        self.label_id = self.dialog.findChild(QLabel, 'label_id')
