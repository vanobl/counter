import os
from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate
from classies.show_invoice import ShowInvoice
from classies.show_service import ShowService

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QTableWidget, QWidget, QLabel
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
from PySide2.QtCore import QFile, Qt

from PySide2 import QtGui, QtCore, QtWidgets

from classies.edit_invoicing import EditInvoicing
from classies.edit_incoming_acts import EditIncomingActs

# импортируем таблицы
from db.alchemy import Acts, str_to_date, Counterparties, ProductService, ServiceActs, Invoice, ServiceInvoice

# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class IncomingActs(QWidget):
    def __init__(self, parent=None):
        super(IncomingActs, self).__init__(parent)
        self.path = os.path.join('faces', 'invoicing.ui')

        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        # определим лэйауты
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.g_layout = QGridLayout()

        # определим элементы управления
        self.label = self.dialog.findChild(QLabel, 'label')
        self.table_bill = self.dialog.findChild(QTableWidget, 'table_bill')
        self.btn_add = self.dialog.findChild(QPushButton, 'btn_add')
        self.btn_changed = self.dialog.findChild(QPushButton, 'btn_changed')
        self.btn_delete = self.dialog.findChild(QPushButton, 'btn_delete')

        # назначим подсказки для элементов
        self.btn_add.setToolTip('Добавить акт')
        self.btn_changed.setToolTip('Изменить акт')
        self.btn_delete.setToolTip('Удалить акт')

        # назначим действия для объектов
        self.btn_add.clicked.connect(self.add_act)
        self.btn_changed.clicked.connect(self.edit_act)
        self.btn_delete.clicked.connect(self.dell_act)

        # задаём специальные размеров колонок
        self.table_bill.setColumnWidth(0, 80)  # дата
        self.table_bill.setColumnWidth(1, 80)  # сумма
        self.table_bill.setColumnWidth(2, 160)  # контрагент
        # колонка "комментарий" использует остаток пространства

        # применим горизонтальный расlayout
        self.h_layout.addWidget(self.btn_add)
        self.h_layout.addWidget(self.btn_changed)
        self.h_layout.addWidget(self.btn_delete)
        # добавим спайсер
        self.h_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # заполним вертикальный layout
        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.table_bill)
        self.v_layout.addLayout(self.h_layout)

        self.g_layout.addLayout(self.v_layout, 0, 0)

        # применим сетку к окну
        self.setLayout(self.g_layout)

        # зададим размер окна
        self.resize(640, 480)

        self.btn_changed.setEnabled(False)

        self.period = []
        self.id_acts = []

        self.filling_table()

    # метод формирование надписи
    def change_period(self):
        query_list = conn.query(Acts).filter(Acts.date_acts).all()
        data_list = []
        for elem in query_list:
            data_list.append(elem.date_acts.strftime("%d.%m.%Y"))
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

    # метод добавление данных в новую строку в окне edit_invoicing
    def set_data_table_service(self, data: list):
        rows = self.win.table_service.rowCount()
        self.win.table_service.setRowCount(int(rows + 1))
        columns = self.win.table_service.columnCount()
        for i in range(0, columns):
            item = QtWidgets.QTableWidgetItem(str(data[i]))
            self.win.table_service.setItem(rows, i, item)

    # метод заполнения таблицы
    def filling_table(self):
        self.table_bill.setRowCount(int(0))  # удаляем строки
        items = conn.query(Acts).all()
        self.id = []
        for item in items:
            # пересохраняем объект таблицы в строчку
            row = []
            self.id.append(item.id)
            row.append(item.date_acts.strftime("%d.%m.%Y"))
            row.append(item.summ_acts)
            name_company = conn.query(Counterparties).filter(Counterparties.id == item.id_company).first().name_c
            row.append(name_company)
            row.append(item.comment_acts)
            # вставляем строчку в таблицу
            self.set_data_in_new_row(row)
        self.change_period()

    # Возвращает список значений строки таблицы
    def get_value_row(self, current_row):
        value_cells = []
        if self.table_bill.isItemSelected(current_row):
            index_row = self.table_bill.row(current_row)
            columns = self.table_bill.columnCount()
            for column in range(0, columns):
                value_cells.append(self.table_bill.item(index_row, column).text())
        return value_cells

    # кнопки главного окна:
    def add_act(self):  # метод добавления акта
        self.open_show_invoice_window()

    def edit_act(self):  # метод редактирования акта
        if self.table_bill.isItemSelected(self.table_bill.currentItem()):
            self.work_with_service('edit')

    def dell_act(self):   # метод удаления выделиной строки
        if self.table_bill.isItemSelected(self.table_bill.currentItem()):
            self.work_with_service('dell')

    # функционал главного окна "просмотр актов" (incomming acts)
    def open_show_invoice_window(self):
        self.show_inv_win = ShowInvoice('add')
        self.show_inv_win.setWindowTitle('Выбрать выписку')
        self.show_inv_win.setWindowModality(Qt.ApplicationModal)
        self.show_inv_win.setWindowFlags(Qt.Window)
        self.show_inv_win.show()
        self.show_inv_win.btn_changed.clicked.connect(self.select_invoice)

    # кнопка 2-го окна
    def select_invoice(self):  # метод выбора счёта
        if self.show_inv_win.table_bill.isItemSelected(self.show_inv_win.table_bill.currentItem()):
            self.open_show_service_window()

    # функционал 2-го окна "Просмотр выписок" (show_invoice)
    def open_show_service_window(self):
        print('открыто через главное окно')
        self.show_ser_win = ShowService('add')
        self.show_ser_win.setWindowTitle('Выбрать услуги')
        self.show_ser_win.setWindowModality(Qt.ApplicationModal)
        self.show_ser_win.setWindowFlags(Qt.Window)
        self.show_ser_win.show()
        # ищем id выбранного счёта
        id_invoice = self.show_inv_win.selected_invoice()

        # заполняем таблицу в 3-м окне
        self.show_ser_win.filling_table(id_invoice)
        self.show_ser_win.btn_add.clicked.connect(self.select_service)

    # кнопка 3-го окна
    def select_service(self):  # метод выбора услуг
        if self.show_ser_win.table_service.isItemSelected(self.show_ser_win.table_service.currentItem()):
            self.add_services_in_act()

    def add_services_in_act(self):
        # получаем id выбранного счёта
        id_invoice = self.show_inv_win.selected_invoice()
        selected_invoice = conn.query(Invoice).filter(Invoice.id == id_invoice).first()
        # создаём новый акт (таблица Acts)
        d = self.show_ser_win.date_edit.text()
        new_act = Acts(
            id_company=selected_invoice.id_company,
            date_acts=str_to_date(d),
            summ_acts=0,  # обновляется после сохранения услуг
            comment_acts=self.show_ser_win.comment_edit.text())
        conn.add(new_act)
        conn.commit()

        # ищем последний id из таблицы Invoice
        result = conn.query(Acts.id).all()
        last_act_id = result[-1].id
        # получаем id выбраных услуг
        id_services = self.show_ser_win.get_id_selected_services()

        prices = []
        for id in id_services:
            # считываем параметры выбранной услуги из БД
            print(id)
            query_id = conn.query(ServiceInvoice).filter(ServiceInvoice.id == id).first()
            amount = query_id.amount_service
            price = query_id.price_service
            # сохраняем стоимость для вычисления суммы
            prices.append(price * amount)
            new_service_invoice = ServiceActs(
                id_acts=last_act_id,
                id_service=query_id.id_service,
                amount_service=amount,
                price_service=price)
            conn.add(new_service_invoice)
            conn.commit()
            # Обновляем сумму счёта
        conn.query(Acts).filter(Acts.id == last_act_id).update({'summ_acts': sum(prices)})
        conn.commit()
        self.show_ser_win.close()
        self.show_inv_win.close()
        self.filling_table()
