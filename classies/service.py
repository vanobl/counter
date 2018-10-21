import os

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QListWidget, QWidget
from PySide2.QtCore import QFile, Qt

from classies.edit_service import EditService

# импортируем таблицы
from db.alchemy import ProductService

# создадим сессию
conn = Connect().get_session()

inner = Communicate()


class Service(QWidget):
    def __init__(self, parent=None):
        super(Service, self).__init__(parent)
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
        self.btn_add.setToolTip('Добавить продукт (услугу)')
        self.btn_changed.setToolTip('Изменить продукт (услугу)')
        self.btn_delete.setToolTip('Удалить продукт (услугу)')

        # назначим действия для объектов
        self.btn_add.clicked.connect(self.insert_service)
        self.btn_changed.clicked.connect(self.edit_service)
        self.btn_delete.clicked.connect(self.dell_service)

        # запускаем заполнение таблицы
        self.filling_list()

    # метод заполнения списка компаний
    def filling_list(self):
        # выполняем запрос
        services = conn.query(ProductService).all()
        # очищаем список
        self.list_company.clear()
        # заполняем список
        for item in services:
            self.list_company.addItem(item.name_service)

    # метод отображения окна
    def work_with_service(self, selector):
        query_service = ''
        self.name_service = ''  # для редактирования названия услуг
        self.win = EditService(selector)
        if selector == 'add':
            self.win.setWindowTitle('Добавление продукта, услуги')
        elif selector == 'edit':
            self.win.setWindowTitle('Редактирование продукта, услуги')
            selected_list = self.list_company.selectedItems()
            for ls in selected_list:
                self.name_service = ls.text()
            query_service = conn.query(ProductService).filter_by(
                name_service=self.name_service).first()
            self.win.edit_name.setText(query_service.name_service)
        elif selector == 'dell':
            selected_list = self.list_company.selectedItems()
            for ls in selected_list:
                self.name_service = ls.text()
            query_service = conn.query(ProductService).filter_by(
                name_service=self.name_service).first()
            conn.query(ProductService).filter(
                ProductService.id == query_service.id).delete()
            conn.commit()
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_action.clicked.connect(self.add_upt_dell)
        self.win.btn_exit.clicked.connect(self.win.close)
        self.win.show()

    # метод модального окна "Редактирование продукта, услуги"
    def add_upt_dell(self):
        if self.win.action == 'add':
            new_service = ProductService(self.win.edit_name.text())
            conn.add(new_service)
            conn.commit()
            self.win.close()
            self.filling_list()
        elif self.win.action == 'edit':
            conn.query(ProductService).filter(
                ProductService.name_service == self.name_service
            ).update({'name_service': self.win.edit_name.text()})
            conn.commit()
            self.win.close()
            self.filling_list()

    # метод добавления услуг
    def insert_service(self):
        self.work_with_service('add')

    # метод редактирования услуг
    def edit_service(self):
        self.work_with_service('edit')

    # метод удаления услуг
    def dell_service(self):
        service_list = self.list_company.selectedItems()
        name_service = ''
        for item in service_list:
            name_service = item.text()
        query_service = conn.query(ProductService).filter_by(
            name_service=name_service).first()
        conn.query(ProductService).filter(
            ProductService.id == query_service.id).delete()
        conn.commit()
        self.filling_list()
