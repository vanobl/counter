import os
from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QTableWidget, QWidget, QLabel
from PySide2.QtCore import QFile, Qt

from PySide2 import QtGui, QtCore, QtWidgets

from classies.edit_invoicing import EditInvoicing

# импортируем таблицы
from db.alchemy import Invoice, str_to_date, Counterparties, ProductService, ServiceInvoice

# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class Invoicing(QWidget):
    def __init__(self, parent=None):
        super(Invoicing, self).__init__(parent)
        self.path = os.path.join('faces', 'invoicing.ui')

        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        # определим элементы управления
        self.label = self.dialog.findChild(QLabel, 'label')
        self.table_bill = self.dialog.findChild(QTableWidget, 'table_bill')
        self.btn_add = self.dialog.findChild(QPushButton, 'btn_add')
        self.btn_changed = self.dialog.findChild(QPushButton, 'btn_changed')
        self.btn_delete = self.dialog.findChild(QPushButton, 'btn_delete')

        # назначим подсказки для элементов
        self.btn_add.setToolTip('Добавить счёт')
        self.btn_changed.setToolTip('Изменить счёт')
        self.btn_delete.setToolTip('Удалить счёт')

        # назначим действия для объектов
        self.btn_add.clicked.connect(self.insert_service)
        self.btn_changed.clicked.connect(self.edit_service)
        self.btn_delete.clicked.connect(self.dell_service)

        # задаём специальные размеров колонок
        self.table_bill.setColumnWidth(0, 80)  # дата
        self.table_bill.setColumnWidth(1, 80)  # сумма
        self.table_bill.setColumnWidth(2, 160)  # контрагент
        # колонка "комментарий" использует остаток пространства 

        self.period = []
        self.id = []

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

    # метод добавление данных в новую строку в окне edit_invoicing
    def set_data_table_service(self, data: list):
        rows = self.win.table_service.rowCount()
        print(rows)
        self.win.table_service.setRowCount(int(rows + 1))
        columns = self.win.table_service.columnCount()
        print(columns)
        for i in range(0, columns):
            item = QtWidgets.QTableWidgetItem(str(data[i]))
            self.win.table_service.setItem(rows, i, item)


    # метод заполнения таблицы
    def filling_table(self):
        self.table_bill.setRowCount(int(0))  # удаляем строки
        items = conn.query(Invoice).all()
        self.id = []
        for item in items:
            # пересохраняем объект таблицы в строчку
            row = []
            self.id.append(item.id)
            row.append(item.date_invoice.strftime("%d.%m.%Y"))
            row.append(item.summ_invoice)
            name_company = conn.query(Counterparties).filter(Counterparties.id==item.id_company).first().name_c
            row.append(name_company)
            row.append(item.comment_invoice)
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

    # метод текущего окна
    def work_with_service(self, selector):
        self.win = EditInvoicing(selector)
        self.id_selected_row = ''  # ID выделенной строки
        if selector == 'add':
            self.win.setWindowTitle('Добавить счёт')
        else:  # удаление и редактирование
            # получаем значения ячеек выделенной строки
            selected_row = self.table_bill.currentItem()
            value_cells = self.get_value_row(selected_row)
            # ищем id записи
            index_row = self.table_bill.row(selected_row)
            self.id_selected_row = self.id[index_row]
            # получаем id из таблицы invoice
            query_invoice = conn.query(Invoice).filter(Invoice.id == self.id_selected_row)
            id_invoice = query_invoice.first().id
            # получаем все услуги по текущему счёту
            query_service_invoice = conn.query(ServiceInvoice).filter(
                ServiceInvoice.id_invoice == id_invoice)
            if selector == 'dell':
                query_invoice.delete()
                conn.commit()
                query_service_invoice.delete()
                conn.commit()
                self.filling_table()
            elif selector == 'edit':
                # вставляем данных из таблицы invoice
                d = query_invoice.first().date_invoice
                self.win.date_edit.setDate(d)  # дата
                self.win.comment_edit.setText(query_invoice.first().comment_invoice)  # коммент
                # компания
                id_company = query_invoice.first().id_company
                name_company = conn.query(Counterparties).filter(Counterparties.id == id_company).first().name_c
                for i in range(self.win.cmbox_company.count()):
                    if self.win.cmbox_company.itemText(i) == name_company:
                        self.win.cmbox_company.setCurrentIndex(i)
                # вставляем данных из таблицы service_invoice
                services = query_service_invoice.all()
                for index_row in range(0, len(services)):
                    service_value = []
                    # наименование услуг
                    id_service = services[index_row].id_service
                    name_service = conn.query(ProductService).filter(
                        ProductService.id == id_service).first().name_service
                    service_value.append(name_service)
                    # количество
                    amount = services[index_row].amount_service
                    service_value.append(amount)
                    # цена
                    price = services[index_row].price_service
                    service_value.append(price)
                    # стоимость
                    summ = int(amount) * int(price)
                    service_value.append(str(summ))
                    # вставляем данные
                    self.set_data_table_service(service_value)
        self.start_win()

    # запуск окна
    def start_win(self):
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_save.clicked.connect(self.add_upt_dell)
        self.win.show()

    def get_company_id(self):
        current_name = self.win.cmbox_company.currentText()
        result = conn.query(Counterparties).filter(Counterparties.name_c == current_name).first()
        return result.id

    # метод модального окна "Добавить счёт"
    def add_upt_dell(self):
        if self.win.action == 'save':
            # считываем данные сохранения в таблицу Invoice
            name_company = self.win.cmbox_company.currentText()
            id_company = conn.query(Counterparties).filter(Counterparties.name_c==name_company).first().id
            d = self.win.date_edit.text()
            comment = self.win.comment_edit.text()
            # сохраняем в базу (таблица Invoice)
            new_invoice = Invoice(
                id_company=id_company,
                date_invoice=str_to_date(d),
                summ_invoice=0,  # обновляется после сохранения услуг
                comment_invoice=comment)
            conn.add(new_invoice)
            conn.commit()

            # ищем последний id из таблицы Invoice
            result = conn.query(Invoice.id).all()
            last_id = result[-1].id

            # определяем количество строк в таблице (услуг)
            rows = self.win.table_service.rowCount()
            prices = []
            for row in range(0, rows):
                # считываем данные из таблицу окна с услугами
                name_service = self.win.table_service.item(row, 0).text()
                id_service = conn.query(ProductService).filter(ProductService.name_service == name_service).first().id
                amount_service = int(self.win.table_service.item(row, 1).text())
                price_service = float(self.win.table_service.item(row, 2).text())
                prices.append(int(self.win.table_service.item(row, 3).text()))
                # сохраняем в базу
                new_service_invoice = ServiceInvoice(
                    id_invoice=last_id,
                    id_service=id_service,
                    amount_service=amount_service,
                    price_service=price_service)
                conn.add(new_service_invoice)
                conn.commit()
            # Обновляем сумму счёта
            conn.query(Invoice).filter(Invoice.id == last_id).update({'summ_invoice': sum(prices)})
            conn.commit()
        elif self.win.action == 'edit':
            pass
        self.win.close()
        self.filling_table()
        self.change_period()

    # сохранение услуг
    def save_service(self):
        self.work_with_service('save')

    # метод добавления услуг
    def insert_service(self):
        self.work_with_service('add')

    # метод редактирования услуг
    def edit_service(self):
        if self.table_bill.isItemSelected(self.table_bill.currentItem()):
            self.work_with_service('edit')

    # метод удаления виделеной строки
    def dell_service(self):
        if self.table_bill.isItemSelected(self.table_bill.currentItem()):
            self.work_with_service('dell')
