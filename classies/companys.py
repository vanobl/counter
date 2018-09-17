import os

from classies.connect import Connect
from classies.comunicate import Communicate
from classies.edit_company import EditCompany

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QListWidget, QWidget
from PySide2.QtCore import QFile, Qt

# импортируем таблицы
from db.alchemy import Company
# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class Companys(QWidget):
    def __init__(self, parent=None):
        super(Companys, self).__init__(parent)
        self.path = os.path.join('faces', 'company.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        # определим элементы управления
        self.list_company = self.dialog.findChild(QListWidget, 'list_company')
        self.btn_add = self.dialog.findChild(QPushButton, 'btn_add')
        self.btn_changed = self.dialog.findChild(QPushButton, 'btn_changed')
        self.btn_delete = self.dialog.findChild(QPushButton, 'btn_delete')

        # назначим подсказки для элементов
        self.btn_add.setToolTip('Добавить организацию')
        self.btn_changed.setToolTip('Редактировать организацию')
        self.btn_delete.setToolTip('Удалить организацию')

        # назначим действия для объектов
        self.btn_add.clicked.connect(self.insert_company)
        self.btn_changed.clicked.connect(self.edit_company)
        self.btn_delete.clicked.connect(self.dell_company)

        # запускаем заполнение таблицы
        self.filling_list()

    # метод заполнения списка компаний
    def filling_list(self):
        # выполняем запрос
        companys = conn.query(Company).all()
        # очищаем список
        self.list_company.clear()
        # заполняем список
        for company in companys:
            self.list_company.addItem(company.namecompany)

    # метод отображения окна
    def work_with_company(self, selector):
        query_company = ''
        self.win = EditCompany(selector)
        if selector == 'add':
            self.win.setWindowTitle('Добавление компании')
        elif selector == 'edit':
            self.win.setWindowTitle('Редактирование компании')
            name_company = ''
            list = self.list_company.selectedItems()
            for ls in list:
                name_company = ls.text()
            query_company = conn.query(Company).filter_by(
                namecompany=name_company).first()
            self.win.edit_company.setText(query_company.namecompany)
            self.win.edit_inn.setText(query_company.inn)
            self.win.edit_ogrn.setText(query_company.ogrn)
            self.win.edit_address.setText(query_company.adress)
            self.win.label_id.setNum(query_company.id)
        elif selector == 'dell':
            list = self.list_company.selectedItems()
            for ls in list:
                name_company = ls.text()
            query_company = conn.query(Company).filter_by(
                namecompany=name_company).first()
            conn.query(Company).filter(
                Company.id == query_company.id).delete()
            conn.commit()
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_action.clicked.connect(self.add_upt_dell)
        self.win.btn_exit.clicked.connect(self.win.close)
        self.win.show()

    # метод работы с компаниями
    def add_upt_dell(self):
        if self.win.action == 'add':
            # print(self.win.action)
            new_company = Company(self.win.edit_company.text(),
                                  self.win.edit_inn.text(),
                                  self.win.edit_ogrn.text(),
                                  self.win.edit_address.text())
            conn.add(new_company)
            conn.commit()
            self.win.close()
            self.filling_list()
        elif self.win.action == 'edit':
            conn.query(Company).filter(
                Company.id == self.win.label_id.text()
            ).update({'namecompany': self.win.edit_company.text(),
                'inn': self.win.edit_inn.text(),
                'ogrn': self.win.edit_ogrn.text(),
                'adress': self.win.edit_address.text()})
            conn.commit()
            self.win.close()
            self.filling_list()
        elif self.win.action == 'dell':
            # print(self.list_company.is)
            pass

    # метод добавления компании
    def insert_company(self):
        self.work_with_company('add')

    # метод редактирования компании
    def edit_company(self):
        self.work_with_company('edit')

    # метод удаления компании
    def dell_company(self):
        # self.work_with_company('dell')
        list = self.list_company.selectedItems()
        for ls in list:
            name_company = ls.text()
        query_company = conn.query(Company).filter_by(
            namecompany=name_company).first()
        conn.query(Company).filter(Company.id == query_company.id).delete()
        conn.commit()
        self.filling_list()

    # @Slot(str)
    def update(self, text):
        # self.filling_list()
        print(text)

    def widget_exit(self):
        self.win.close()
