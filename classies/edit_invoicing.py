import os, re


from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget, QTableWidget, QComboBox, QDateEdit
from PySide2.QtCore import QFile, QDate, Qt
from PySide2 import QtGui, QtCore, QtWidgets
from classies.service_for_invoice import ServiceForInvoice

from db.alchemy import Counterparties, Invoice, str_to_date, ProductService
# создадим сессию
conn = Connect().get_session()

over = Communicate()


class EditInvoicing(QWidget):
    def __init__(self, parent=None):
        super(EditInvoicing, self).__init__(parent)
        self.path = os.path.join('faces', 'edit_invoicing.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        # определим элементы управления
        self.date_edit = self.dialog.findChild(QDateEdit, 'date_edit')
        self.table_service = self.dialog.findChild(QTableWidget, 'table_service')
        self.table_total = self.dialog.findChild(QTableWidget, 'table_total')
        self.cmbox_company = self.dialog.findChild(QComboBox, 'cmbox_company')
        self.btn_save = self.dialog.findChild(QPushButton, 'btn_save')
        self.btn_add = self.dialog.findChild(QPushButton, 'btn_add')
        self.btn_changed = self.dialog.findChild(QPushButton, 'btn_changed')
        self.btn_delete = self.dialog.findChild(QPushButton, 'btn_delete')

        # назначим подсказки для элементов
        self.btn_save.setToolTip('Сохранить счёт')
        self.btn_add.setToolTip('Добавить услугу, товар')
        self.btn_changed.setToolTip('Изменить услугу, товар')
        self.btn_delete.setToolTip('Удалить услугу, товар')

        # задаём специальные размеров колонок основной таблицы
        self.table_service.setColumnWidth(0, 329)  # наименование услуг
        self.table_service.setColumnWidth(1, 100)  # количество
        self.table_service.setColumnWidth(2, 100)  # цена
        self.table_service.setColumnWidth(3, 100)  # сумма

        # задаём специальные размеров колонок итоговой таблицы
        self.table_total.setColumnWidth(0, 549)  # наименование услуг
        self.table_total.setColumnWidth(1, 80)  # количество

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
        self.btn_add.clicked.connect(self.insert_service)
        self.btn_changed.clicked.connect(self.edit_service)
        self.btn_delete.clicked.connect(self.dell_service)

    # метод добавление данных в новую строку
    def set_data_in_new_row(self, data: list):
        rows = self.table_service.rowCount()
        self.table_service.setRowCount(int(rows + 1))
        columns = self.table_service.columnCount()
        for i in range(0, columns):
            item = QtWidgets.QTableWidgetItem(str(data[i]))
            self.table_service.setItem(rows, i, item)

    # метод добавление данных в текущую строку
    def set_data_in_current_row(self, data: list):
        selected_row = self.table_service.currentItem()
        id_row = self.table_service.row(selected_row)
        columns = self.table_service.columnCount()
        for i in range(0, columns):
            item = QtWidgets.QTableWidgetItem(str(data[i]))
            self.table_service.setItem(id_row, i, item)

    # Возвращает список значений строки таблицы
    def get_value_row(self, current_row):
        value_cells = []
        if self.table_service.isItemSelected(current_row):
            index_row = self.table_service.row(current_row)
            columns = self.table_service.columnCount()
            for column in range(0, columns):
                value_cells.append(self.table_service.item(index_row, column).text())
        return value_cells

    # мктод суммирования стоимости услуг
    def total_summ(self):
        # собираем значения последних ячеек по строкам
        value_cells = []
        columns = self.table_service.columnCount()
        rows = self.table_service.rowCount()
        for row in range(0, rows):
            print(row)
            value = self.table_service.item(row, columns-1).text()
            value_cells.append(int(value))
        summ = sum(value_cells)
        # вставляем сумму
        self.table_total.horizontalHeaderItem(1).setText(str(summ))

    # метод заполнения таблицы
    def filling_table(self, row):
        self.table_service.setRowCount(int(0))  # удаляем строки
        # items = conn.query(Invoice).all()
        # self.id = []
        # #d = item.date_invoice.strftime("%d.%m.%Y")
        # for item in items:
        #     # пересохраняем объект таблицы в строчку
        #     row = []
        #     name = item.id_service
        #     amount = int(item.amount_service)
        #     price = int(item.price_service)
        #     summ = amount * price
        #
        #     self.id.append(item.id)
        #     row.append(name)
        #     row.append(amount)
        #     row.append(price)
        #     row.append(summ)
            # вставляем строчку в таблицу
        self.set_data_in_new_row(row)
            # self.date_edit.setDate()
        # self.change_period()

    # метод отображения окна
    def work_with_service(self, selector):
        self.win = ServiceForInvoice(selector)
        self.id_selected_row = ''  # ID выделенной строки
        if selector == 'add':
            self.win.setWindowTitle('Добавить выписку')
            self.start_win()
        else:
            # получаем выделенную строку
            selected_row = self.table_service.currentItem()
            if selector == 'dell':
                id_row = self.table_service.row(selected_row)
                self.table_service.removeRow(id_row)
            elif selector == 'edit':
                # получаем значения ячеек выделенной строки
                value_cells = self.get_value_row(selected_row)
                # вставляем исходные значения: название услуги
                for i in range(self.win.cmbox_service.count()):
                    if self.win.cmbox_service.itemText(i) == value_cells[0]:
                        self.win.cmbox_service.setCurrentIndex(i)

                self.win.amount_service.setText(value_cells[1])  # количество
                self.win.price_service.setText(value_cells[2])  # количество
                self.start_win()

    # запуск окна
    def start_win(self):
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_action.clicked.connect(self.add_upt_dell)
        self.win.btn_exit.clicked.connect(self.win.close)
        self.win.show()

    # метод модального окна "Дорбавления услуг"
    def add_upt_dell(self):
        if self.win.action == 'add' or self.win.action == 'edit':
            # получаем данные из дочернего окна:
            new_service = [self.win.cmbox_service.currentText(),
                           self.win.amount_service.text(),
                           self.win.price_service.text(),
                           self.win.summ_service.text()]
            # вставляем данные а таблицу
            if self.win.action == 'edit':
                # вставляем данные в туже строку
                self.set_data_in_current_row(new_service)
            else:
                self.set_data_in_new_row(new_service)
            self.win.close()
            self.total_summ()

        # self.change_period()

    # метод добавления услуг
    def insert_service(self):
        self.work_with_service('add')

    # метод редактирования услуг
    def edit_service(self):
        if self.table_service.isItemSelected(self.table_service.currentItem()):
            self.work_with_service('edit')

    # метод удаления виделеной строки
    def dell_service(self):
        if self.table_service.isItemSelected(self.table_service.currentItem()):
            self.work_with_service('dell')
