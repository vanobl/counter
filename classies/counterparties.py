import os

from classies.connect import Connect
from classies.comunicate import Communicate
from classies.edit_counterpartie import EditCounterpartie

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QListWidget, QWidget
from PySide2.QtCore import QFile, Qt

# импортируем таблицы
from db.alchemy import Counterparties
# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class Counterpartie(QWidget):
    def __init__(self, parent=None):
        super(Counterpartie, self).__init__(parent)
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
        self.btn_add.setToolTip('Добавить контрагента')
        self.btn_changed.setToolTip('Редактировать контрагента')
        self.btn_delete.setToolTip('Удалить контрагента')

        # назначим действия для объектов
        self.btn_add.clicked.connect(self.insert_counterpartie)
        self.btn_changed.clicked.connect(self.edit_counterpartie)
        self.btn_delete.clicked.connect(self.dell_counterpartie)

        # запускаем заполнение таблицы
        self.filling_list()

    # метод заполнения списка компаний
    def filling_list(self):
        # выполняем запрос
        companys = conn.query(Counterparties).all()
        # очищаем список
        self.list_company.clear()
        # заполняем список
        for company in companys:
            self.list_company.addItem(company.name_c)

    # метод отображения окна
    def work_with_counterpartie(self, selector):
        query_counterpartie = ''
        self.win = EditCounterpartie(selector)
        if selector == 'add':
            self.win.setWindowTitle('Добавление компании')
        elif selector == 'edit':
            self.win.setWindowTitle('Редактирование компании')
            name_company = ''
            list = self.list_company.selectedItems()
            for ls in list:
                name_company = ls.text()
            query_counterpartie = conn.query(
                Counterparties).filter_by(name_c=name_company).first()
            self.win.edit_company.setText(query_counterpartie.name_c)
            self.win.edit_inn.setText(query_counterpartie.inn_c)
            self.win.edit_ogrn.setText(query_counterpartie.ogrn_c)
            self.win.edit_address.setText(query_counterpartie.adress_c)
            self.win.edit_name_bank.setText(query_counterpartie.bank_c)
            self.win.edit_bik.setText(query_counterpartie.bik_c)
            self.win.edit_ks.setText(query_counterpartie.ks_c)
            self.win.edit_rs.setText(query_counterpartie.rs_c)
            self.win.label_id.setNum(query_counterpartie.id)
        elif selector == 'dell':
            list = self.list_company.selectedItems()
            for ls in list:
                name_company = ls.text()
            query_company = conn.query(Counterparties).filter_by(
                namecompany=name_company).first()
            conn.query(Counterparties).filter(
                Counterparties.id == query_company.id).delete()
            conn.commit()
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_action.clicked.connect(self.add_upt_dell)
        self.win.btn_exit.clicked.connect(self.win.close)
        self.win.show()

    # метод работы с компаниями
    def add_upt_dell(self):
        if self.win.action == 'add':
            print(self.win.action)
            new_company = Counterparties(
                self.win.edit_company.text(),
                self.win.edit_inn.text(),
                self.win.edit_ogrn.text(),
                self.win.edit_address.text(),
                self.win.edit_name_bank.text(),
                self.win.edit_bik.text(),
                self.win.edit_ks.text(),
                self.win.edit_rs.text())
            conn.add(new_company)
            conn.commit()
            self.win.close()
            self.filling_list()
        elif self.win.action == 'edit':
            conn.query(Counterparties).filter(
                Counterparties.id == self.win.label_id.text()
            ).update({'name_c': self.win.edit_company.text(),
                      'inn_c': self.win.edit_inn.text(),
                      'ogrn_c': self.win.edit_ogrn.text(),
                      'adress_c': self.win.edit_address.text(),
                      'bank_c': self.win.edit_name_bank.text(),
                      'bik_c': self.win.edit_bik.text(),
                      'ks_c': self.win.edit_ks.text(),
                      'rs_c': self.win.edit_rs.text()})
            conn.commit()
            self.win.close()
            self.filling_list()
        # elif self.win.action == 'dell':
        #     #print(self.list_company.is)
        #     pass

    # метод добавления контрагента
    def insert_counterpartie(self):
        self.work_with_counterpartie('add')

    # метод редактирования компании
    def edit_counterpartie(self):
        self.work_with_counterpartie('edit')

    # метод удаления компании
    def dell_counterpartie(self):
        # self.work_with_company('dell')
        list = self.list_company.selectedItems()
        for ls in list:
            name_company = ls.text()
        query_company = conn.query(Counterparties).filter_by(
            name_c=name_company).first()
        conn.query(Counterparties).filter(
            Counterparties.id == query_company.id).delete()
        conn.commit()
        self.filling_list()
