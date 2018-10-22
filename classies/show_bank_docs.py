import os
import sys
import subprocess
import time
from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QWidget, QLabel, QDateEdit, QComboBox
from PySide2.QtCore import QFile, Qt, QDate

from py3o.template import Template


from PySide2 import QtGui, QtCore, QtWidgets

from classies.edit_bank_docs import EditBankDocs

from db.alchemy import BankDocsRev, str_to_date, Counterparties


# создадим сессию
conn = Connect().get_session()

inner = Communicate()

class Item(object):
    pass

class ShowBankDocs(QWidget):
    def __init__(self, parent=None):
        super(ShowBankDocs, self).__init__(parent)
        self.path = os.path.join('faces', 'show_bank_docs.ui')

        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()



        # определим элементы управления
        self.label = self.dialog.findChild(QLabel, 'label')
        self.date_start = self.dialog.findChild(QDateEdit, 'date_start')
        self.date_end = self.dialog.findChild(QDateEdit, 'date_end')
        self.cmbox_company = self.dialog.findChild(QComboBox, 'cmbox_company')
        self.cmbox_action = self.dialog.findChild(QComboBox, 'cmbox_action')
        self.btn_create = self.dialog.findChild(QPushButton, 'btn_create')

        # назначим подсказки для элементов
        self.btn_create.setToolTip('Сформировать отчёт')

        # добавляем значения по умолчанию: текущую дату
        self.date_start.setDate(QDate.currentDate())
        self.date_end.setDate(QDate.currentDate())
        # список контроагентов
        result = conn.query(Counterparties).all()
        if result:
            for elem in result:
                self.cmbox_company.addItem(str(elem.name_c))

        # назначим действия для объектов
        self.btn_create.clicked.connect(self.create_report)

        self.setMaximumHeight(225)
        self.setMaximumWidth(473)

    def create_report(self):
        # собираем условия с формы
        # name_company = self.cmbox_company.currentText()
        # id_company = conn.query(Counterparties).filter(Counterparties.name_c == name_company).first().id

        # data_start = self.date_start.text()
        # data_end = self.date_end.text()
        # action = self.cmbox_action.currentText()  # приход / расход
        # формируем запрос в базу
        bank_query = conn.query(BankDocsRev).filter(BankDocsRev.date_docs >= self.date_start.date().toPython()).filter(BankDocsRev.date_docs <= self.date_end.date().toPython()).filter(BankDocsRev.action_docs == self.cmbox_action.currentText()).all()
        for item in bank_query:
            print(f'Контрагент: {item.p_counterparties.name_c}, сумма: {item.summ_docs:.2f}, статус документа: {item.action_docs}')
        # определяем пути к файлам
        path_empty = os.path.join('templates', 'report_bank.ods')
        path_full = os.path.join('temp', 'report_bank.ods')
        t = Template(path_empty, path_full)

        items = list()
        total_summ = 0

        # перебираем значения из запроса
        for bank in bank_query:
            item = Item()
            item.date = bank.date_docs.strftime('%d.%m.%Y')
            # item.summ = str(round(bank.summ_docs, 2)).replace('.', ',')
            item.summ = round(bank.summ_docs, 2)
            item.counterp = bank.p_counterparties.name_c
            item.coment = bank.comment_docs
            items.append(item)
            total_summ += bank.summ_docs
        
        # формируем даты
        start_date = Item()
        start_date.date = datetime.strftime(self.date_start.date().toPython(), '%d.%m.%Y')

        end_date = Item()
        end_date.date = datetime.strftime(self.date_end.date().toPython(), '%d.%m.%Y')

        total = Item()
        # total.summ = str(round(total_summ, 2)).replace('.', ',')
        total.summ = round(total_summ, 2)
        
        # группируем данные для передачи в отчёт
        date = dict(items = items, start_date = start_date, end_date = end_date, total = total)

        # передаём данные в отчёт
        t.render(date)

        # открываем созданный отчёт
        if sys.platform == "win32":
                os.startfile(path_full)
        else:
            opener ="open" if sys.platform == "darwin" else "xdg-open"
            subprocess.call([opener, path_full])