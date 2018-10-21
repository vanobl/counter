import os

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget, QComboBox, QDateEdit, QTextEdit, QCheckBox
from PySide2.QtCore import QFile, QDate

from db.alchemy import BankDocsRev
# создадим сессию
conn = Connect().get_session()

over = Communicate()


class EditBankDocs(QWidget):
    def __init__(self, action, parent=None):
        super(EditBankDocs, self).__init__(parent)
        self.path = os.path.join('faces', 'edit_bank_docs.ui')
        self.ui_file = QFile(self.path)
        self.ui_file.open(QFile.ReadOnly)
        self.loader = QUiLoader()
        self.dialog = self.loader.load(self.ui_file, self)
        self.ui_file.close()

        self.action = action

        # определим элементы управления
        self.date_edit = self.dialog.findChild(QDateEdit, 'date_edit')
        self.summ_edit = self.dialog.findChild(QLineEdit, 'summ_edit')
        self.cmbox_action = self.dialog.findChild(QComboBox, 'cmbox_action')
        self.combo_counterparties = self.dialog.findChild(QComboBox, 'combo_counterparties')
        self.combo_byudget = self.dialog.findChild(QComboBox, 'combo_byudget')
        self.check_byudget = self.dialog.findChild(QCheckBox, 'check_byudget')
        self.comment_edit = self.dialog.findChild(QTextEdit, 'comment_edit')
        self.number_doc_edit = self.dialog.findChild(QLineEdit, 'number_doc_edit')
        self.btn_action = self.dialog.findChild(QPushButton, 'btn_action')
        self.btn_exit = self.dialog.findChild(QPushButton, 'btn_exit')

        # добавляем значения по умолчанию: текущую дату
        self.date_edit.setDate(QDate.currentDate())
        # порядковый номер докумета 
        last_row = conn.query(BankDocsRev).order_by(BankDocsRev.id.desc()).first()
        if last_row:
            h = self.number_doc_edit.setText(str(last_row.number_docs + 1))

        # назначим подсказки для элементов
        self.btn_action.setToolTip('Сохранить')
        self.btn_exit.setToolTip('Отменить')

        # сделаем элементы не активными
        self.combo_byudget.setEnabled(False)
        self.check_byudget.setEnabled(False)

