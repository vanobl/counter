import os
import sys
import subprocess
import xlwings
import time

from datetime import datetime

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget, QComboBox, QDateEdit, QTextEdit, QCheckBox, QLabel
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
from PySide2.QtCore import QFile, QDate

from py3o.template import Template

from classies.connect import Connect
from db.alchemy import Company as table_company
from db.alchemy import BankDocsRev as table_bank

# создадим сессию
conn = Connect().get_session()

class Item(object):
    pass

class Declaration(QWidget):
    def __init__(self, parent=None):
        super(Declaration, self).__init__(parent)
        self.path = os.path.join('faces', 'report_declaration.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        # определим компоненты
        self.label_year = self.dialog.findChild(QLabel, 'label_year')
        self.date_year = self.dialog.findChild(QDateEdit, 'date_year')
        self.btn_create = self.dialog.findChild(QPushButton, 'btn_create')

        # назначим действия для объектов
        self.btn_create.clicked.connect(self.create_report)

        # определим лэйауты
        self.h_layout = QHBoxLayout()
        self.g_layout = QGridLayout()

        # применим layouts
        self.h_layout.addWidget(self.label_year)
        self.h_layout.addWidget(self.date_year)
        self.h_layout.addWidget(self.btn_create)

        self.g_layout.addLayout(self.h_layout, 0, 0)

        self.setLayout(self.g_layout)
    
    # метод формирования отчёта
    def create_report(self):
        #для работы с Excel
        company_query = conn.query(table_company).first()
        # # определяем пути к файлам
        path_empty = os.path.join('templates', 'report_declaration.xls')
        path_full = os.path.join('temp', 'report_declaration.xls')

        workbook = xlwings.Book(path_empty)
        worksheet = workbook.sheets['стр.1']
        worksheet2 = workbook.sheets['стр.2_Разд.1.1']
        worksheet3 = workbook.sheets['стр.4_Разд.2.1.1']

        # формируем список ИНН
        inn = []
        for n in company_query.inn:
            inn.append(n)
            inn.append('')
            inn.append('')

        # заполняем ИНН
        if len(company_query.inn) == 10:
            worksheet.range('AK1').value = inn
            worksheet.range(f'BO1').value = 0
            worksheet.range(f'BR1').value = 0
        elif len(company_query.inn) == 12:
            worksheet.range(f'AK1').value = inn
        
        # заполняем номер корректировки
        worksheet.range(f'Y12').value = '0'
        worksheet.range(f'AB12').value = '0'
        worksheet.range(f'AE12').value = '1'

        # заполняем налоговый период
        worksheet.range(f'BU12').value = '3'
        worksheet.range(f'BX12').value = '4'

        # заполняем отчётный год
        year_str = str(self.date_year.date().year())
        year = []
        for y in year_str:
            year.append(y)
            year.append('')
            year.append('')
        worksheet.range(f'DE12').value = year

        # заполняем налоговый орган
        nalog_org = []
        for nal in company_query.inspection:
            nalog_org.append(nal)
            nalog_org.append('')
            nalog_org.append('')
        worksheet.range(f'AN14').value = nalog_org

        # заполняем по месту нахождения
        nah = ['2', '', '', '1', '', '', '0']
        worksheet.range(f'DH14').value = nalog_org

        # заполняем наименование компании
        if len(company_query.namecompany) <= 40:
            name_company = []
            for name in company_query.namecompany:
                name_company.append(name)
                name_company.append('')
                name_company.append('')
            worksheet.range(f'A16').value = name_company
        
        # заполняем ОКВЭД
        okved = []
        for i in company_query.okved:
            okved.append(i)
            okved.append('')
            okved.append('')
        worksheet.range(f'BI24').value = okved

        # заполняем дату декларации
        datt = []
        for i in str(time.strftime('%d.%m.%Y')):
            datt.append(i)
            datt.append('')
            datt.append('')
        worksheet.range(f'AE63').value = datt

        # доходы 1 квартал
        bank_query_income_1 = conn.query(table_bank).filter(table_bank.date_docs >= datetime.strptime(f'{str(self.date_year.date().year())}.1.1', '%Y.%m.%d').date()).filter(table_bank.date_docs <= datetime.strptime(f'{str(self.date_year.date().year())}.3.31', '%Y.%m.%d').date()).filter(table_bank.action_docs == 'Приход').all()
        # print(bank_query)
        total_1 = 0
        for i in bank_query_income_1:
            total_1 =+ round(i.summ_docs, 0)
        total_str_1 = []
        for i in str(total_1):
            total_str_1.append(i)
            total_str_1.append('')
            total_str_1.append('')
        worksheet3.range(f'CC22').value = total_str_1

        workbook.save(path_full)

        