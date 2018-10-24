import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, create_engine,\
    Date, Float, ForeignKey
from sqlalchemy.orm import relationship


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
    inspection = Column(String)
    okved = Column(String)
    phone = Column(String)
    oktmo = Column(String)

    def __init__(self, namecompany, inn, ogrn, adress, inspection, okved, phone, oktmo):
        self.namecompany = namecompany
        self.inn = inn
        self.ogrn = ogrn
        self.adress = adress
        self.inspection = inspection
        self.okved = okved
        self.phone = phone
        self.oktmo = oktmo

    def __repr__(self):
        return f'Company: {self.namecompany}, INN: {self.inn}, OGRN: {self.ogrn}, ADDRESS: {self.adress}, INSPECTION {self.inspection}, OKVED {self.okved}, PHONE {self.phone}, OKTMO {self.oktmo}'

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
    date_docs = Column(Date, nullable=False)
    summ_docs = Column(Float(10, 2), nullable=False)
    action_docs = Column(String, nullable=False)
    comment_docs = Column(String)
    counterparties_id = Column(Integer, ForeignKey('counterparties.id'))
    byudgetpay_id = Column(Integer, ForeignKey('byudget_pay.id'), nullable=True, default=None)

    # определим ссылки на таблицы
    p_counterparties = relationship('Counterparties', foreign_keys=[counterparties_id])
    p_byudgetpay = relationship('ByudgetPay', foreign_keys=[byudgetpay_id])

    def __init__(self, number_docs, date_docs, summ_docs, action_docs, comment_docs, counterparties_id, byudgetpay_id):
        self.number_docs = number_docs
        self.date_docs = date_docs
        self.summ_docs = summ_docs
        self.action_docs = action_docs
        self.comment_docs = comment_docs
        self.counterparties_id = counterparties_id
        self.byudgetpay_id= byudgetpay_id
    
    def __repr__(self):
        return f'Документ: №{self.number_docs}, {self.action_docs} от {self.date_docs}, на сумму {self.summ_docs}, коментарий {self.comment_docs}'

# определим класс таблицы детализации платежей в бюджет
class ByudgetPay(CBase):
    # имя таблицы
    __tablename__ = 'byudget_pay'

    # поля таблицы
    id = Column(Integer, primary_key=True)
    name_byudget = Column(String(255), nullable=False)

    def __init__(self, name_byudget):
        self.name_byudget = name_byudget
    
    def __repr__(self):
        return f'Наименование отчисления {self.name_byudget}'

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


class Invoice(CBase):
    # имя таблицы
    __tablename__ = 'invoice'

    # поля таблицы счетов
    id = Column(Integer, primary_key=True)
    id_company = Column(Integer, ForeignKey('counterparties.id'), nullable=False)
    date_invoice = Column(Date, nullable=False)
    summ_invoice = Column(Float, nullable=False)
    comment_invoice = Column(String, nullable=True)

    def __init__(self, id_company, date_invoice, comment_invoice, summ_invoice):
        self.id_company = id_company
        self.date_invoice = date_invoice
        self.comment_invoice = comment_invoice
        self.summ_invoice = summ_invoice

class ServiceInvoice(CBase):
    # имя таблицы
    __tablename__ = 'service_invoice'

    # поля таблицы счетов
    id = Column(Integer, primary_key=True)
    id_invoice = Column(Integer, ForeignKey('invoice.id'), nullable=False)  # группировка услуг в сёте
    id_service = Column(Integer, ForeignKey('product_service.id'), nullable=True)
    amount_service = Column(Integer, nullable=True)
    price_service = Column(Float, nullable=True)

    def __init__(self, id_invoice, id_service, amount_service, price_service):
        self.id_invoice = id_invoice
        self.id_service = id_service
        self.amount_service = amount_service
        self.price_service = price_service

class Acts(CBase):
    # имя таблицы
    __tablename__ = 'acts'

    # поля таблицы счетов
    id = Column(Integer, primary_key=True)
    id_company = Column(Integer, ForeignKey('counterparties.id'), nullable=False)
    date_acts = Column(Date, nullable=False)
    summ_acts = Column(Float, nullable=False)
    comment_acts = Column(String, nullable=True)

    def __init__(self, id_company, date_acts, comment_acts, summ_acts):
        self.id_company = id_company
        self.date_acts = date_acts
        self.comment_acts = comment_acts
        self.summ_acts = summ_acts

class ServiceActs(CBase):
    # имя таблицы
    __tablename__ = 'service_act'

    # поля таблицы счетов
    id = Column(Integer, primary_key=True)
    id_acts = Column(Integer, ForeignKey('acts.id'), nullable=False)  # группировка услуг в сёте
    id_service = Column(Integer, ForeignKey('product_service.id'), nullable=True)
    amount_service = Column(Integer, nullable=True)
    price_service = Column(Float, nullable=True)

    def __init__(self, id_acts, id_service, amount_service, price_service):
        self.id_acts = id_acts
        self.id_service = id_service
        self.amount_service = amount_service
        self.price_service = price_service

# конвертер для дата полученных из виджетов
def str_to_date(datestr="", format="%d.%m.%Y"):
    from datetime import datetime
    if not datestr:
        return datetime.today().date()
    return datetime.strptime(datestr, format).date()

# применим изменения
CBase.metadata.create_all(engine)