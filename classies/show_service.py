import os, re


from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget, QTableWidget, QComboBox, QDateEdit, QLabel
from PySide2.QtCore import QFile, QDate, Qt
from PySide2 import QtGui, QtCore, QtWidgets


from db.alchemy import Counterparties, Invoice, str_to_date, ProductService, ServiceInvoice
# создадим сессию
conn = Connect().get_session()

over = Communicate()

# ???????????? МОЖЕТ ВНЕДРИТЬ ID СЧЁТА В АТРИБУТ КЛАССА ??????????

class ShowService(QWidget):
    def __init__(self, action, parent=None):
        super(ShowService, self).__init__(parent)
        self.path = os.path.join('faces', 'edit_invoicing.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        self.action = action

        # определим элементы управления
        self.label_data = self.dialog.findChild(QLabel, 'label_data')
        self.date_edit = self.dialog.findChild(QDateEdit, 'date_edit')
        self.table_service = self.dialog.findChild(QTableWidget, 'table_service')
        self.comment_edit = self.dialog.findChild(QLineEdit, 'comment_edit')
        self.table_total = self.dialog.findChild(QTableWidget, 'table_total')
        self.cmbox_company = self.dialog.findChild(QComboBox, 'cmbox_company')
        self.btn_save = self.dialog.findChild(QPushButton, 'btn_save')
        self.btn_add = self.dialog.findChild(QPushButton, 'btn_add')
        self.btn_changed = self.dialog.findChild(QPushButton, 'btn_changed')
        self.btn_delete = self.dialog.findChild(QPushButton, 'btn_delete')
        self.label_commet = self.dialog.findChild(QLabel, 'label_comment')

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

        # список контроагентов
        result = conn.query(Counterparties).all()
        if result:
            for elem in result:
                self.cmbox_company.addItem(str(elem.name_c))

        # вставляем текущую дату
        self.date_edit.setDate(QDate.currentDate())

        # назначим подсказки для элементов
        self.btn_add.setToolTip('Добавить')

        # убираем не нужные
        self.btn_save.hide()
        self.btn_delete.hide()
        self.btn_changed.hide()

        # отключаем выбор:
        self.cmbox_company.setEnabled(False)  # контрагентов

        # переменовываем
        self.btn_add.setText('Добавит в акт')
        self.label_commet.setText('Комментарий к акту')
        self.label_data.setText('Акт от ')


        self.id_services = []  # ID данных загружаемых из таблицы ServiceInvoice

    # метод добавление данных в новую строку
    def set_data_in_new_row(self, data: list):
        rows = self.table_service.rowCount()
        self.table_service.setRowCount(int(rows + 1))
        columns = self.table_service.columnCount()
        for i in range(0, columns):
            item = QtWidgets.QTableWidgetItem(str(data[i]))
            self.table_service.setItem(rows, i, item)

    # метод суммирования стоимости услуг
    def total_summ(self):
        # собираем значения последних ячеек по строкам
        value_cells = []
        columns = self.table_service.columnCount()
        rows = self.table_service.rowCount()
        for row in range(0, rows):
            value = self.table_service.item(row, columns-1).text()
            value_cells.append(float(value))
        summ = sum(value_cells)
        # вставляем сумму
        self.table_total.horizontalHeaderItem(1).setText(str(summ))

    # метод заполнения таблицы
    def filling_table(self, id_invoice: int):
        # ищем все услуги по счёту
        services = conn.query(ServiceInvoice).filter(ServiceInvoice.id_invoice == id_invoice).all()
        for service in services:
            # сохраняем id услугу
            self.id_services.append(service.id)
            name_service = conn.query(ProductService).filter(ProductService.id == service.id_service).first().name_service
            amount = service.amount_service
            price = service.price_service
            summ = int(amount) * int(price)
            # вставляем данные в таблицу
            self.set_data_in_new_row([name_service, amount, price, summ])
        self.total_summ()  # отображаем сумму
        self.set_company(id_invoice)  # вставляем дату

    def set_company(self, id_invoice: int):
        invoice = conn.query(Invoice).filter(Invoice.id == id_invoice).first()
        # ищем название компании
        name_company = conn.query(Counterparties).filter(Counterparties.id == invoice.id_company).first().name_c
        # вставляем компанию
        for i in range(self.cmbox_company.count()):
            if self.cmbox_company.itemText(i) == name_company:
                self.cmbox_company.setCurrentIndex(i)

    def get_id_selected_services(self):
        # определяем выделенные строчки в таблице окна с услугами
        selected_items = self.table_service.selectedItems()
        result = []
        for item in selected_items:
            # получаем строку
            selected_row = self.table_service.row(item)
            # находим id усллуги
            id = self.id_services[selected_row]
            result.append(id)
        return result
