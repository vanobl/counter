import os

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QListWidget, QWidget
from PySide2.QtCore import QFile, Qt

from classies.connect import Connect
from classies.edit_service import EditService

# импортируем таблицы
from db.alchemy import ByudgetPay

# создадим сессию
conn = Connect().get_session()

class Budget(QWidget):
    def __init__(self, parent=None):
        super(Budget, self).__init__(parent)
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
        self.btn_add.setToolTip('Добавить бюджет')
        self.btn_changed.setToolTip('Изменить бюджет')
        self.btn_delete.setToolTip('Удалить бюджет')

        # назначим действия для объектов
        self.btn_add.clicked.connect(self.insert_budget)
        self.btn_changed.clicked.connect(self.edit_budget)
        self.btn_delete.clicked.connect(self.dell_budget)

        # запускаем заполнение таблицы
        self.filling_list()
    

    # метод заполнения списка компаний
    def filling_list(self):
        # выполняем запрос
        budgets = conn.query(ByudgetPay).all()
        # очищаем список
        self.list_company.clear()
        # заполняем список
        for item in budgets:
            self.list_company.addItem(item.name_byudget)
    
    # метод модального окна "Редактирование продукта, услуги"
    def add_upt_dell(self):
        if self.win.action == 'add':
            new_budget = ByudgetPay(self.win.edit_name.text())
            conn.add(new_budget)
            conn.commit()
            self.win.close()
            self.filling_list()
        elif self.win.action == 'edit':
            conn.query(ByudgetPay).filter(ByudgetPay.name_byudget == self.name_budget).update({'name_byudget': self.win.edit_name.text()})
            conn.commit()
            self.win.close()
            self.filling_list()
    
    # метод отображения окна
    def work_with_service(self, selector):
        self.win = EditService(selector)
        self.name_budget = ''
        if selector == 'add':
            self.win.setWindowTitle('Добавление бюджета')
        elif selector == 'edit':
            self.win.setWindowTitle('Редактирование бюджета')
            selected_list = self.list_company.selectedItems()
            for ls in selected_list:
                self.name_budget = ls.text()
                print(self.name_budget)
                query_budget = conn.query(ByudgetPay).filter_by(name_byudget=self.name_budget).first()
                self.win.edit_name.setText(query_budget.name_byudget)
        
        self.win.setWindowModality(Qt.ApplicationModal)
        self.win.setWindowFlags(Qt.Window)
        self.win.btn_action.clicked.connect(self.add_upt_dell)
        self.win.btn_exit.clicked.connect(self.win.close)
        self.win.show()
    

    # метод добавления бюджета
    def insert_budget(self):
        self.work_with_service('add')
    
    # метод редактирование бюджета
    def edit_budget(self):
        self.work_with_service('edit')
    
    # метод удаления бюджета
    def dell_budget(self):
        budget_list = self.list_company.selectedItems()
        name_budget = ''
        for item in budget_list:
            name_budget = item.text()
        budget_q = conn.query(ByudgetPay).filter_by(name_byudget = name_budget).first()
        conn.query(ByudgetPay).filter(ByudgetPay.id == budget_q.id).delete()
        conn.commit()
        self.filling_list()