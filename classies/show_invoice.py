import os
from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QTableWidget, QWidget, QLabel
from PySide2.QtCore import QFile, Qt

from PySide2 import QtGui, QtCore, QtWidgets

from classies.show_service import ShowService

# импортируем таблицы
from db.alchemy import Invoice, str_to_date, Counterparties, ProductService, ServiceInvoice, Acts, ServiceActs

# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class ShowInvoice(QWidget):
    def __init__(self, action, parent=None):
        super(ShowInvoice, self).__init__(parent)
        self.path = os.path.join('faces', 'invoicing.ui')

        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        self.action = action

        # определим элементы управления
        self.label = self.dialog.findChild(QLabel, 'label')
        self.table_bill = self.dialog.findChild(QTableWidget, 'table_bill')
        self.btn_add = self.dialog.findChild(QPushButton, 'btn_add')
        self.btn_changed = self.dialog.findChild(QPushButton, 'btn_changed')
        self.btn_delete = self.dialog.findChild(QPushButton, 'btn_delete')

        # назначим подсказки для элементов
        self.btn_changed.setToolTip('Выбрать счёт для создание акта')

        # задаём специальные размеров колонок
        self.table_bill.setColumnWidth(0, 80)  # дата
        self.table_bill.setColumnWidth(1, 80)  # сумма
        self.table_bill.setColumnWidth(2, 160)  # контрагент
        # колонка "комментарий" использует остаток пространства

        # смена названия кнопок
        self.btn_changed.setText('Выбрать')

        # убираем лишние кнопки
        self.btn_add.hide()
        self.btn_delete.hide()

        self.period = []
        self.id_invoices = []  # ID данных загружаемых из таблицы Invoice
        self.filling_table()

    # метод формирование надписи
    def change_period(self):
        query_list = conn.query(Invoice).filter(Invoice.date_invoice).all()
        data_list = []
        for elem in query_list:
            data_list.append(elem.date_invoice.strftime("%d.%m.%Y"))
        data_list.sort(key=lambda d: datetime.strptime(d, '%d.%m.%Y'))
        if data_list:
            first = data_list[0]
            last = data_list[-1]
            self.label.setText(f'C {first} по {last}')

    # метод добавление данных в новую строку
    def set_data_in_new_row(self, data: list):
        rows = self.table_bill.rowCount()
        self.table_bill.setRowCount(int(rows + 1))
        columns = self.table_bill.columnCount()
        for i in range(0, columns):
            item = QtWidgets.QTableWidgetItem(str(data[i]))
            self.table_bill.setItem(rows, i, item)

    # метод заполнения таблицы
    def filling_table(self):
        self.table_bill.setRowCount(int(0))  # удаляем строки
        items = conn.query(Invoice).all()
        self.id_invoices = []
        for item in items:
            # пересохраняем объект таблицы в строчку
            row = []
            self.id_invoices.append(item.id)

            row.append(item.date_invoice.strftime("%d.%m.%Y"))
            row.append(item.summ_invoice)
            name_company = conn.query(Counterparties).filter(Counterparties.id == item.id_company).first().name_c
            row.append(name_company)
            row.append(item.comment_invoice)
            # вставляем строчку в таблицу
            self.set_data_in_new_row(row)
        self.change_period()

    def selected_invoice(self):
        # определяем индекс строки
        selected_row = self.table_bill.currentItem()
        index_row = self.table_bill.row(selected_row)
        result = self.id_invoices[index_row]
        return result