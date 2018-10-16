# -*- coding: utf-8 -*-
from classies.connect import Connect
from classies.companys import Companys
from classies.counterparties import Counterpartie
from classies.service import Service
from classies.bank_docs import BankDocs
from classies.invoicing import Invoicing
from classies.incoming_acts import IncomingActs

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QAction
from PySide2.QtCore import QFile, QObject, Qt

# создадим сессию
conn = Connect().get_session()


class Counter(QObject):
    def __init__(self, uifile, parent=None):
        super(Counter, self).__init__(parent)
        self.ui_file = QFile(uifile)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.window = self.loader.load(self.ui_file)
        self.ui_file.close()

        # определим компоненты управления
        self.select_company = self.window.findChild(QAction, 'select_company')
        self.select_counterparties = self.window.findChild(
            QAction, 'select_counterparties')
        self.select_service = self.window.findChild(QAction, 'select_service')
        self.journal_income_consumption = self.window.findChild(
            QAction, 'journal_income_consumption')
        self.journal_invoicing = self.window.findChild(
            QAction, 'journal_invoicing')
        self.journal_acts = self.window.findChild(
            QAction, 'journal_acts')


        # назначим действия для объектов
        self.select_company.triggered.connect(self.read_company)
        self.select_counterparties.triggered.connect(self.read_counterparties)
        self.select_service.triggered.connect(self.read_service)
        self.journal_income_consumption.triggered.connect(self.read_bank_docs)
        self.journal_invoicing.triggered.connect(self.read_invoicing)
        self.journal_acts.triggered.connect(self.read_acts)
        self.window.show()

    # метод открытия окна с компаниями
    def read_company(self):
        self.wincom = Companys()
        self.wincom.setWindowTitle('Компании')
        self.wincom.setWindowModality(Qt.ApplicationModal)
        self.wincom.setWindowFlags(Qt.Window)
        self.wincom.show()

    # метод открытия окна с контрагентами
    def read_counterparties(self):
        self.wincom = Counterpartie()
        self.wincom.setWindowTitle('Контрагенты')
        self.wincom.setWindowModality(Qt.ApplicationModal)
        self.wincom.setWindowFlags(Qt.Window)
        self.wincom.show()

    # метод открытия окна с товарами
    def read_service(self):
        self.wincom = Service()
        self.wincom.setWindowTitle('Продукты, услуги')
        self.wincom.setWindowModality(Qt.ApplicationModal)
        self.wincom.setWindowFlags(Qt.Window)
        self.wincom.show()

    # метод открытия окна выставленые счета
    def read_bank_docs(self):
        self.wincom = BankDocs()
        self.wincom.setWindowTitle('Выписки банка')
        self.wincom.setWindowModality(Qt.ApplicationModal)
        self.wincom.setWindowFlags(Qt.Window)
        self.wincom.show()

    # метод открытия окна выставленые счета
    def read_invoicing(self):
        self.wincom = Invoicing()
        self.wincom.setWindowTitle('Выставленные счета')
        self.wincom.setWindowModality(Qt.ApplicationModal)
        self.wincom.setWindowFlags(Qt.Window)
        self.wincom.show()

    # метод открытия окна выставленые акты
    def read_acts(self):
        self.wincom = IncomingActs()
        self.wincom.setWindowTitle('Выставленные акты')
        self.wincom.setWindowModality(Qt.ApplicationModal)
        self.wincom.setWindowFlags(Qt.Window)
        self.wincom.show()

