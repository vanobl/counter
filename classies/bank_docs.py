import os
from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QTableWidget, QWidget, QLabel
from PySide2.QtCore import QFile, Qt

from PySide2 import QtGui, QtCore, QtWidgets

from classies.edit_bank_docs import EditBankDocs


from db.alchemy import BankDocsRev, str_to_date


# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class BankDocs(QWidget):
    def __init__(self, parent=None):
        super(BankDocs, self).__init__(parent)
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

        # замена имени колонки в форме
        self.table_bill.horizontalHeaderItem(2).setText('Действие')
        
        # задаём специальные размеров колонок
        self.table_bill.setColumnWidth(0, 100)  # дата
        self.table_bill.setColumnWidth(1, 100)  # сумма
        self.table_bill.setColumnWidth(2, 100)  # действие
        self.table_bill.setColumnWidth(3, 240)  # комментарий

        self.period = []
        self.id = []

        self.filling_table()

    # метод формирование надписи
    def change_period(self):
        query_list = conn.query(BankDocsRev).filter(BankDocsRev.date_docs).all()
        data_list = []
        for elem in query_list:
            data_list.append(elem.date_docs.strftime("%d.%m.%Y"))
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
        self.table_bill.setRowCount(int(0)) # удаляем строки
        items = conn.query(BankDocsRev).all()
        self.id = []
        for item in items:
            # пересохраняем объект таблицы в строчку
            row = []
            self.id.append(item.id)
            row.append(item.date_docs.strftime("%d.%m.%Y"))
            row.append(item.summ_docs)
            row.append(item.action_docs)
            row.append(item.comment_docs)
            # вставляем строчку в таблицу 
            self.set_data_in_new_row(row)
        self.change_period()

    def get_value_row(self, current_row):
        """ Возвращает список значений строки таблицы"""
        value_cells = [] 
        if self.table_bill.isItemSelected(current_row):
            index_row = self.table_bill.row(current_row)
            columns = self.table_bill.columnCount()
            for column in range(0, columns):
                value_cells.append(self.table_bill.item(index_row, column).text())
        return value_cells

    # метод отображения окна
    def work_with_service(self, selector):
        self.win = EditBankDocs(selector)
        self.id_selected_row = ''  # ID выделенной строки
        if selector == 'add':
            self.win.setWindowTitle('Добавить выписку')
            self.start_win()
        else:
            # получаем значения ячеек выделенной строки
            selected_row = self.table_bill.currentItem()
            value_cells = self.get_value_row(selected_row)
            # ищем id записи
            index_row = self.table_bill.row(selected_row)
            self.id_selected_row = self.id[index_row]
            # формируем запрос в таблицу
            result = conn.query(BankDocsRev).filter(BankDocsRev.id == self.id_selected_row)
            if selector == 'dell':
                result.delete()
                conn.commit()
                self.filling_table()
            elif selector == 'edit':
                nmbr_doc = result.one().number_docs
                # вставляем исходные значения
                self.win.number_doc_edit.setText(str(nmbr_doc))  #  номер 
                d = str_to_date(value_cells[0])
                self.win.date_edit.setDate(d)  # дата
                self.win.summ_edit.setText(value_cells[1])  # сумма
                # приход / расход
                for i in range(self.win.cmbox_action.count()):
                    if self.win.cmbox_action.itemText(i) == value_cells[2]:
                        self.win.cmbox_action.setCurrentIndex(i)
                self.win.comment_edit.setText(value_cells[3])  # комментарий
                self.start_win()

    # запуск окна
    def start_win(self):
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_action.clicked.connect(self.add_upt_dell)
        self.win.btn_exit.clicked.connect(self.win.close)
        self.win.show()

    # метод модального окна "Редактирование банковские выписки"
    def add_upt_dell(self):
        if self.win.action == 'add':
            d = self.win.date_edit.text()
            self.period.append(d)
            new_doc = BankDocsRev(
                int(self.win.number_doc_edit.text()),
                str_to_date(d),
                int(self.win.summ_edit.text()),
                self.win.cmbox_action.currentText(),
                self.win.comment_edit.toPlainText())
            conn.add(new_doc)
            conn.commit()
            self.win.close()
        elif self.win.action == 'edit':
            conn.query(BankDocsRev).filter(
                BankDocsRev.id == self.id_selected_row
            ).update({'number_docs': self.win.number_doc_edit.text(),
                'date_docs': str_to_date(self.win.date_edit.text()),
                'summ_docs': float(self.win.summ_edit.text()),
                'action_docs': self.win.cmbox_action.currentText(),
                'comment_docs': self.win.comment_edit.toPlainText()})
            conn.commit()
        self.win.close()
        self.filling_table()
        self.change_period()

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
