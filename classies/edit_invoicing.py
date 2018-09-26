import os, re


from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget, QTableWidget, QComboBox, QDateEdit
from PySide2.QtCore import QFile, QDate

from db.alchemy import Counterparties
# создадим сессию
conn = Connect().get_session()

over = Communicate()


class EditInvoicing(QWidget):
    def __init__(self, action, parent=None):
        super(EditInvoicing, self).__init__(parent)
        self.path = os.path.join('faces', 'edit_invoicing.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        self.action = action

        # определим элементы управления
        self.date_edit = self.dialog.findChild(QDateEdit, 'date_edit')
        self.table_service = self.dialog.findChild(QTableWidget, 'table_service')
        self.cmbox_company = self.dialog.findChild(QComboBox, 'cmbox_company')
        self.btn_add = self.dialog.findChild(QPushButton, 'btn_add')
        self.btn_changed = self.dialog.findChild(QPushButton, 'btn_changed')
        self.btn_delete = self.dialog.findChild(QPushButton, 'btn_delete')
        # назначим подсказки для элементов
        self.btn_add.setToolTip('Добавить услугу, товар')
        self.btn_changed.setToolTip('Изменить услугу, товар')
        self.btn_delete.setToolTip('Удалить услугу, товар')

        # задаём специальные размеров колонок
        self.table_service.setColumnWidth(0, 329)  # наименование услуг
        self.table_service.setColumnWidth(1, 100)  # количество
        self.table_service.setColumnWidth(2, 100)  # цена
        self.table_service.setColumnWidth(3, 100)  # сумма

        # добавляем значения по умолчанию: текущую дату
        self.date_edit.setDate(QDate.currentDate())
        # список контроагентов
        result = conn.query(Counterparties).all()
        if result:
            for elem in result:
                self.cmbox_company.addItem(str(elem.name_c))

        # назначим подсказки для элементов
        self.btn_add.setToolTip('Добавить')
        self.btn_delete.setToolTip('Удалить')

        # назначим действия для объектов
        # self.btn_add.clicked.connect(self.insert_service)
        # self.btn_changed.clicked.connect(self.edit_service)
        # self.btn_delete.clicked.connect(self.dell_service)

        # запускаем заполнение таблицы
        self.filling_table()

    # метод заполнения списка компаний
    def filling_table(self):
        pass





