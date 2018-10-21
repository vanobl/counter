import os
from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QWidget, QLabel, QDateEdit, QComboBox
from PySide2.QtCore import QFile, Qt, QDate


from PySide2 import QtGui, QtCore, QtWidgets

from classies.edit_bank_docs import EditBankDocs

from db.alchemy import BankDocsRev, str_to_date, Counterparties


# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class ShowBankDocs(QWidget):
    def __init__(self, parent=None):
        super(ShowBankDocs, self).__init__(parent)
        self.path = os.path.join('faces', 'show_bank_docs.ui')

        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        # определим элементы управления
        self.label = self.dialog.findChild(QLabel, 'label')
        self.date_start = self.dialog.findChild(QDateEdit, 'date_start')
        self.date_end = self.dialog.findChild(QDateEdit, 'date_end')
        self.cmbox_company = self.dialog.findChild(QComboBox, 'cmbox_company')
        self.cmbox_action = self.dialog.findChild(QComboBox, 'cmbox_action')
        self.btn_create = self.dialog.findChild(QPushButton, 'btn_create')

        # назначим подсказки для элементов
        self.btn_create.setToolTip('Сформировать отчёт')

        # добавляем значения по умолчанию: текущую дату
        self.date_start.setDate(QDate.currentDate())
        self.date_end.setDate(QDate.currentDate())
        # список контроагентов
        result = conn.query(Counterparties).all()
        if result:
            for elem in result:
                self.cmbox_company.addItem(str(elem.name_c))

        # назначим действия для объектов
        self.btn_create.clicked.connect(self.create_report)

    def create_report(self):
        # собираем условия с формы
        name_company = self.cmbox_company.currentText()
        id_company = conn.query(Counterparties).filter(Counterparties.name_c == name_company).first().id

        data_start = self.date_start.text()
        data_end = self.date_end.text()
        action = self.cmbox_action.currentText()  # приход / расход






