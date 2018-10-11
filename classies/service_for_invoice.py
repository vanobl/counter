import os, re


from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget, QTableWidget, QComboBox, QDateEdit
from PySide2.QtCore import QFile, QDate

from db.alchemy import ProductService
# создадим сессию
conn = Connect().get_session()

over = Communicate()


class ServiceForInvoice(QWidget):
    def __init__(self, action, parent=None):
        super(ServiceForInvoice, self).__init__(parent)
        self.path = os.path.join('faces', 'service_for_invoice .ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        self.action = action

        # определим элементы управления
        self.cmbox_service = self.dialog.findChild(QComboBox, 'cmbox_service')
        self.amount_service = self.dialog.findChild(QLineEdit, 'amount_service')
        self.price_service = self.dialog.findChild(QLineEdit, 'price_service')
        self.summ_service = self.dialog.findChild(QLineEdit, 'summ_service')
        self.btn_action = self.dialog.findChild(QPushButton, 'btn_action')
        self.btn_exit = self.dialog.findChild(QPushButton, 'btn_exit')

        # назначим подсказки для элементов
        self.btn_action.setToolTip('Добавить услугу, товар')
        self.btn_exit.setToolTip('Отмена')

        # заполняем список улуг
        result = conn.query(ProductService).all()
        if result:
            for elem in result:
                self.cmbox_service.addItem(str(elem.name_service))

        # назначаем события
        self.amount_service.textChanged.connect(self.change_summ)
        self.price_service.textChanged.connect(self.change_summ)

    def change_summ(self):
        amount = self.amount_service.text()
        price = self.price_service.text()
        if amount and price:
            summ = int(amount) * int(price)
            self.summ_service.setText(str(summ))
