#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float,\
    Boolean, create_engine, relationship

Base = declarative_base()
engine = create_engine(f'sqlite:///{os.path.join("db", "counter.db")}')


class Company(Base):
    '''
    таблица с основными данными о компании
    флаг owner - true: базовый пользователь
    false: конрагент
    можно учесть в контроллере возможность выбирать базового пользователя
    при запуске приложения, тогда можно будет использовать одну базу для
    нескольких компаний
    '''

    __tablename__ = 'company'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    inn = Column(Integer)
    ogrn = Column(Integer)
    address = Column(String(250))
    owner = Column(Boolean)

    def __init__(self, name, inn, ogrn, address):
        self.name = name
        self.inn = inn
        self.ogrn = ogrn
        self.address = address


class CompanyAccount(Base):
    # таблица с реквизитами компании

    __tablename__ = 'companyaccount'
    id = Column(Integer, primary_key=True)
    id_company = Column(Integer, ForeignKey('company.id'))
    id_bank = Column(Integer, ForeignKey('banks.id'))
    rs = Column(Integer)

    company = relationship('Company', backref='company')
    bank = relationship('Banks', backref='banks')

    def __init__(self, id_company, id_bank, rs):
        self.id_company = id_company
        self.id_bank = id_bank
        self.rs = rs


class Banks(Base):
    # таблица определяющая все банки

    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    bank_name = Column(String(64), nullable=False)
    bik = Column(Integer)
    ks = Column(Integer)
    address_b = Column(String(250))

    def __init__(self, bank_name, bik, ks, address_b):
        self.bank_name = bank_name
        self.bik = bik
        self.ks = ks
        self.address_b = address_b


class Products(Base):

    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    description = Column(String(200), nullable=False)
    price = Column(Float)

    def __init__(self, description, price=None):
        self.description = description
        self.price = price


class Documents(Base):

    __tablename__ = 'documents'
    doc_number = Column(String(32))
    product = Column(Integer, ForeignKey('products.id'))
    qtty = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)

    def __init__(self, doc_number, product, qtty, price):
        self.doc_number = doc_number
        self.product = product
        self.qtty = qtty
        self.price = price


class IncommingDoc(Base):
    __tablename__ = 'incomming_doc'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('company.id'))
    counterparty = Column(Integer, ForeignKey('company.id'))
    doc_number = Column(String, ForeignKey('documents.doc_number'))
    doc_type = Column(Integer, ForeignKey('doc_type.id'))
    date = Column(Date, nullable=False)
    number_doc_close = Column(String, ForeignKey('outcomming_doc.id'))

    def __init__(self, owner, counterparty, doc_number,
                 doc_type, date, number_doc_close):
        self.owner = owner
        self.counterparty = counterparty
        self.doc_number = doc_number
        self.doc_type = doc_type
        self.date = date
        self.number_doc_close = number_doc_close


class OutcommingDoc(Base):
    __tablename__ = 'outcomming_doc'
    id = Column(Integer, primary_key=True)
    owner = Column(Integer, ForeignKey('company.id'))
    counterparty = Column(Integer, ForeignKey('company.id'))
    doc_number = Column(String, ForeignKey('documents.doc_number'))
    doc_type = Column(Integer, ForeignKey('doc_type.id'))
    date = Column(Date, nullable=False)
    number_doc_close = Column(String, ForeignKey('incomming_doc.id'))

    def __init__(self, owner, counterparty, doc_number,
                 doc_type, date, number_doc_close):
        self.owner = owner
        self.counterparty = counterparty
        self.doc_number = doc_number
        self.doc_type = doc_type
        self.date = date
        self.number_doc_close = number_doc_close


class DocType(Base):

    __tablename__ = 'doc_type'
    id = Column(Integer, primary_key=True)
    description = Column(String, nullable=False)

    def __init__(self, description):
        self.description = description

