import os

from classies.connect import Connect
from classies.comunicate import Communicate

from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import QPushButton, QLineEdit, QWidget, QComboBox, QDateEdit, QTextEdit, QCheckBox, QLabel
from PySide2.QtWidgets import QHBoxLayout, QVBoxLayout, QGridLayout, QSpacerItem, QSizePolicy
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

        # определим лэйауты
        self.h_layout_date_num = QHBoxLayout()
        self.h_layout_action = QHBoxLayout()
        self.h_layout_counterparties = QHBoxLayout()
        self.h_layout_budget = QHBoxLayout()
        self.h_layout_summ = QHBoxLayout()
        self.h_layout_btn = QHBoxLayout()
        self.v_layout_coment = QVBoxLayout()
        self.v_layout_all = QVBoxLayout()
        self.g_layout = QGridLayout()

        # определим надписи для компонентов
        self.label_date = self.dialog.findChild(QLabel, 'label_date')
        self.label_number_doc = self.dialog.findChild(QLabel, 'label_number_doc')
        self.label_action = self.dialog.findChild(QLabel, 'label_action')
        self.label_counterparties = self.dialog.findChild(QLabel, 'label_counterparties')
        self.label_summ = self.dialog.findChild(QLabel, 'label_summ')
        self.label_coment = self.dialog.findChild(QLabel, 'label_coment')

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

        # применим layouts
        self.h_layout_date_num.addWidget(self.label_date)
        self.h_layout_date_num.addWidget(self.date_edit)
        self.h_layout_date_num.addWidget(self.label_number_doc)
        self.h_layout_date_num.addWidget(self.number_doc_edit)
        self.h_layout_date_num.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.h_layout_action.addWidget(self.label_action)
        self.h_layout_action.addWidget(self.cmbox_action)
        self.h_layout_action.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.h_layout_counterparties.addWidget(self.label_counterparties)
        self.h_layout_counterparties.addWidget(self.combo_counterparties)
        self.h_layout_counterparties.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.h_layout_budget.addWidget(self.check_byudget)
        self.h_layout_budget.addWidget(self.combo_byudget)
        self.h_layout_budget.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.h_layout_summ.addWidget(self.label_coment)
        self.h_layout_summ.addWidget(self.summ_edit)
        self.h_layout_summ.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        self.v_layout_coment.addWidget(self.label_coment)
        self.v_layout_coment.addWidget(self.comment_edit)

        self.h_layout_btn.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.h_layout_btn.addWidget(self.btn_action)
        self.h_layout_btn.addWidget(self.btn_exit)

        self.v_layout_all.addLayout(self.h_layout_date_num)
        self.v_layout_all.addLayout(self.h_layout_action)
        self.v_layout_all.addLayout(self.h_layout_counterparties)
        self.v_layout_all.addLayout(self.h_layout_budget)
        self.v_layout_all.addLayout(self.h_layout_summ)
        self.v_layout_all.addLayout(self.v_layout_coment)
        self.v_layout_all.addLayout(self.h_layout_btn)

        self.g_layout.addLayout(self.v_layout_all, 0, 0)

        self.setLayout(self.g_layout)

        self.resize(800, 480)



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

