import os
from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QTableWidget, QWidget, QLabel
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
from PySide2.QtCore import QFile, Qt

from PySide2 import QtGui, QtCore, QtWidgets

from classies.edit_bank_docs import EditBankDocs


from db.alchemy import BankDocsRev, str_to_date
from db.alchemy import Counterparties as table_couterpart
from db.alchemy import ByudgetPay as table_byudget


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

        # определим лэйауты
        self.h_layout_btn = QHBoxLayout()
        self.v_layout = QVBoxLayout()
        self.g_layout = QGridLayout()

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

        # применим растягивание
        self.h_layout_btn.addWidget(self.btn_add)
        self.h_layout_btn.addWidget(self.btn_changed)
        self.h_layout_btn.addWidget(self.btn_delete)

        # добавим спайсер
        self.h_layout_btn.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        
        # вложим горизонтальные лэйауты в вертикальный
        self.v_layout.addWidget(self.label)
        self.v_layout.addWidget(self.table_bill)
        self.v_layout.addLayout(self.h_layout_btn)

        # вложим вертикальный в сетку
        self.g_layout.addLayout(self.v_layout, 0, 0)
        # применим сетку к окну
        self.setLayout(self.g_layout)

        # зададим размер окна
        self.resize(1000, 480)

        # заполним таблицу
        self.filling_table()

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
        self.table_bill.setRowCount(int(0))  # удаляем строки
        items = conn.query(BankDocsRev).all()
        self.id = []
        for item in items:
            # пересохраняем объект таблицы в строчку
            row = []
            self.id.append(item.id)
            row.append(item.date_docs.strftime("%d.%m.%Y"))
            row.append(f'{item.summ_docs:.2f}')
            row.append(item.action_docs)
            row.append(item.comment_docs)
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

    # метод отображения окна
    def work_with_service(self, selector):
        self.win = EditBankDocs(selector)
        self.id_selected_row = ''  # ID выделенной строки
        budget_q = conn.query(table_byudget).all()
        if selector == 'add':
            self.win.setWindowTitle('Добавить выписку')
            # заполним комбобокс контрагентами
            counterpart_q = conn.query(table_couterpart).all()
            for counterp in counterpart_q:
                self.win.combo_counterparties.addItem(counterp.name_c)
            self.start_win()
        else:
            # получаем значения ячеек выделенной строки
            selected_row = self.table_bill.currentItem()
            value_cells = self.get_value_row(selected_row)
            # ищем id записи
            index_row = self.table_bill.row(selected_row)
            self.id_selected_row = self.id[index_row]
            # формируем запрос в таблицу
            result = conn.query(BankDocsRev).filter(BankDocsRev.id == self.id_selected_row).first()
            if selector == 'dell':
                conn.query(BankDocsRev).filter(BankDocsRev.id == self.id_selected_row).delete()
                conn.commit()
                self.filling_table()
            elif selector == 'edit':
                nmbr_doc = result.number_docs
                # вставляем исходные значения
                self.win.number_doc_edit.setText(str(result.number_docs))  # номер
                d = str_to_date(value_cells[0])
                #self.win.date_edit.setDate(d)
                self.win.date_edit.setDate(result.date_docs)  # дата
                self.win.summ_edit.setText(f'{result.summ_docs:.2f}')  # сумма
                # приход / расход
                for i in range(self.win.cmbox_action.count()):
                    if self.win.cmbox_action.itemText(i) == value_cells[2]:
                        self.win.cmbox_action.setCurrentIndex(i)
                # заполним комбобокс контрагентами
                counterpart_q = conn.query(table_couterpart).all()
                for counterp in counterpart_q:
                    self.win.combo_counterparties.addItem(counterp.name_c)
                # установим текущее значение в списке
                self.win.combo_counterparties.setCurrentText(result.p_counterparties.name_c)
                # заполним комбобокс с бюджетами, если нужно
                if result.byudgetpay_id:
                    # ставим галочку
                    self.win.check_byudget.setEnabled(True)
                    self.win.check_byudget.setChecked(True)
                    # заполняем список
                    self.win.combo_byudget.setEnabled(True)
                    for item in budget_q:
                        self.win.combo_byudget.addItem(item.name_byudget)
                    # установим текущее значение в списке
                    self.win.combo_byudget.setCurrentText(result.p_byudgetpay.name_byudget)
                else:
                    pass

                self.win.comment_edit.setText(value_cells[3])  # комментарий
                self.start_win()

    # запуск окна
    def start_win(self):
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_action.clicked.connect(self.add_upt_dell)
        self.win.btn_exit.clicked.connect(self.win.close)
        self.win.cmbox_action.currentTextChanged.connect(self.byudget)
        self.win.check_byudget.stateChanged.connect(self.byudget_pay)
        self.win.show()
    
    # методы для включения/отключения дополнительных полей в выписке
    def byudget(self):
        if self.win.cmbox_action.currentText() == 'Приход':
            self.win.check_byudget.setEnabled(False)
        elif self.win.cmbox_action.currentText() == 'Расход':
            self.win.check_byudget.setEnabled(True)
    
    def byudget_pay(self):
        if self.win.check_byudget.isChecked():
            self.win.combo_byudget.setEnabled(True)
            budget_query = conn.query(table_byudget).all()
            for item in budget_query:
                self.win.combo_byudget.addItem(item.name_byudget)
        else:
            self.win.combo_byudget.clear()
            self.win.combo_byudget.setEnabled(False)

    # метод модального окна "Редактирование банковские выписки"
    def add_upt_dell(self):
        cont_id = conn.query(table_couterpart).filter_by(name_c = self.win.combo_counterparties.currentText()).first()
        byud_q = conn.query(table_byudget).filter_by(name_byudget = self.win.combo_byudget.currentText()).first()
        if self.win.combo_byudget.isEnabled():
            byudget_text = byud_q.id
        else:
            byudget_text = None
            
        if self.win.action == 'add':
            new_doc = BankDocsRev(
                number_docs=int(self.win.number_doc_edit.text()),
                date_docs=self.win.date_edit.date().toPython(),
                summ_docs=float(self.win.summ_edit.text()),
                action_docs=self.win.cmbox_action.currentText(),
                comment_docs=self.win.comment_edit.toPlainText(),
                counterparties_id=cont_id.id,
                byudgetpay_id=byudget_text)
            conn.add(new_doc)
            conn.commit()
            self.win.close()
        elif self.win.action == 'edit':
            conn.query(BankDocsRev).filter(
                BankDocsRev.id == self.id_selected_row
            ).update({'number_docs': self.win.number_doc_edit.text(),
                'date_docs': self.win.date_edit.date().toPython(),
                'summ_docs': float(self.win.summ_edit.text()),
                'action_docs': self.win.cmbox_action.currentText(),
                'comment_docs': self.win.comment_edit.toPlainText(),
                'counterparties_id': cont_id.id,
                'byudgetpay_id': byudget_text})
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
