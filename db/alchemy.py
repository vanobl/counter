import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine,\
    DateTime, Float


import datetime

CBase = declarative_base()
engine = create_engine(f'sqlite:///{os.path.join("db", "counter.db")}')

# http://sqlitebrowser.org/

# определим класс таблицы Компаний


class Company(CBase):
    # имя таблицы
    __tablename__ = 'company'

    # поля таблицы
    id = Column(Integer, primary_key=True)
    namecompany = Column(String, nullable=False, unique=True)
    inn = Column(String, nullable=False)
    ogrn = Column(String, nullable=False)
    adress = Column(String, nullable=False)

    def __init__(self, namecompany, inn, ogrn, adress):
        self.namecompany = namecompany
        self.inn = inn
        self.ogrn = ogrn
        self.adress = adress

    def __repr__(self):
        return 'Company: {}, INN: {}, OGRN: {}, ADDRESS: {}'.format(
            self.namecompany, self.inn, self.ogrn, self.adress)

#определим класс таблицы контрагентов
class Counterparties(CBase):
    #имя таблицы
    __tablename__ = 'counterparties'

    #поля таблицы
    id = Column(Integer, primary_key=True)
    name_c = Column(String, nullable=False, unique=True)
    inn_c = Column(String, nullable=False, unique=True)
    ogrn_c = Column(String, nullable=False, unique=True)
    adress_c = Column(String, nullable=False)
    bank_c = Column(String)
    bik_c = Column(String)
    ks_c = Column(String)
    rs_c = Column(String)

    def __init__(self, name_c, inn_c, ogrn_c, adress_c = '',
                 bank_c = '', bik_c = '', ks_c = '', rs_c = ''):
        self.name_c = name_c
        self.inn_c = inn_c
        self.ogrn_c = ogrn_c
        self.adress_c = adress_c
        self.bank_c = bank_c
        self.bik_c = bik_c
        self.ks_c = ks_c
        self.rs_c = rs_c
    
    def __repr__(self):
        return 'Контрагент: {}, INN: {}, OGRN: {}, ADDR: {},\
        BANK: {}, BIK: {}, KS: {}, RS: {}'.format(
            self.name_c, self.inn_c, self.ogrn_c, self.adress_c,
            self.bank_c, self.bik_c, self.ks_c, self.rs_c)

#определим класс таблицы документов поступлений расходов
class BankDocsRev(CBase):
    #имя таблицы
    __tablename__ = 'bank_docs_rev'

    #поля таблицы
    id = Column(Integer, primary_key=True)
    number_docs = Column(Integer, nullable=False)
    date_docs = Column(DateTime, nullable=False)
    summ_docs = Column(Float, nullable=False)
    action_docs = Column(String, nullable=False)
    comment_docs = Column(String)

    def __init__(self, number_docs, date_docs, summ_docs, action_docs, comment_docs):
        self.number_docs = number_docs
        self.date_docs = date_docs
        self.summ_docs = summ_docs
        self.action_docs = action_docs
        self.comment_docs = comment_docs
    
    def __repr__(self):
        return 'Документ: №{0}, {3} от {1}, на сумму {2}, коментарий {4}'.format(
            self.number_docs, self.date_docs, self.summ_docs, self.action_docs, self.comment_docs)

# определим класс таблицы товаров и услуг
class ProductService(CBase):
    # имя таблицы
    __tablename__ = 'product_service'

    # поля таблицы
    id = Column(Integer, primary_key=True)
    name_service = Column(String, nullable=False)

    def __init__(self, name_service):
        self.name_service = name_service


    def __repr__(self):
        return 'Наименование продукта (услуга): {}'.format(self.name_service)

# конвертер для дата полученных из виджетов
def str_to_date(datestr="", format="%d.%m.%Y"):
    from datetime import datetime
    if not datestr:
        return datetime.today().date()
    return datetime.strptime(datestr, format).date()

# применим изменения
CBase.metadata.create_all(engine)