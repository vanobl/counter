#!/usr/bin/python3
# -*- coding: utf-8 -*-


import os
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Date, Float,\
    create_engine

Base = declarative_base()

engine = create_engine(f'sqlite:///{os.path.join("db", "counter.db")}')


class CompanyAccount(Base):

    __tablename__ = 'companyaccount'

    id = Column(Integer, primary_key=True)

    id_company = Column(Integer, ForeignKey('company.id'))

    id_bank = Column(Integer, ForeignKey('banks.id'))

    ks = Column(Integer)

    rs = Column(Integer)

    def __init__(self, id_company, id_bank, ks, rs):

        self.id_company = id_company

        self.id_bank = id_bank

        self.ks = ks

        self.rs = rs


class Account(Base):

    __tablename__ = 'account'

    id = Column(Integer, primary_key=True)

    id_counterparties = Column(Integer, ForeignKey('counterparties.id'))

    ib_bank = Column(Integer, ForeignKey('banks.id'))

    ks_counterparties = Column(Integer)

    rs_counterparties = Column(Integer)

    def __init__(self, id_counterparties, id_bank,
                 ks_counterparties, rs_counterparties):

        self.id_counterparties = id_counterparties

        self.id_bank = id_bank

        self.ks_counterparties = ks_counterparties

        self.rs_counterparties = rs_counterparties


class Banks(Base):

    __tablename__ = 'banks'

    id = Column(Integer, primary_key=True)

    bank_name = Column(String(64), nullable=False)

    bik = Column(Integer)

    address_b = Column(String(250))

    def __init__(self, bank_name, bik, address_b):

        self.bank_name = bank_name

        self.bik = bik

        self.address_b = address_b


class Company(Base):

    __tablename__ = 'company'

    id = Column(Integer, primary_key=True)

    name = Column(String(64), nullable=False)

    inn = Column(Integer)

    ogrn = Column(Integer)

    address = Column(String(250))

    def __init__(self, name, inn, ogrn, address):

        self.name = name

        self.inn = inn

        self.ogrn = ogrn

        self.address = address


class CounterParties(Base):

    __tablename__ = 'counterparties'

    id = Column(Integer, primary_key=True)

    name_c = Column(String(64), nullable=False)

    inn_c = Column(Integer)

    ogrn_c = Column(Integer)

    address_c = Column(String(250))

    def __init__(self, name_c, inn_c, ogrn_c, address_c):

        self.name_c = name_c

        self.inn_c = inn_c

        self.ogrn_c = ogrn_c

        self.address_c = address_c


class ProductService(Base):

    __tablename__ = 'productservice'

    id = Column(Integer, primary_key=True)

    name_service = Column(String(250))

    def __init__(self, name_service):

        self.name_service = name_service


class BankDocsRev(Base):

    __tablename__ = 'bank_doc_rev'

    id = Column(Integer, primary_key=True)

    id_company = Column(Integer, ForeignKey('company.id'))

    id_counterparties = Column(Integer, ForeignKey('counterparties.id'))

    number_docs = Column(Integer)

    date_docs = Column(Date)

    summ_docs = Column(Float)

    text_docs = Column(String(400))

    id_operation = Column(Integer, ForeignKey('operations.id'))

    def __init__(self, id_company, id_counterparties,
                 number_docs, date_docs, summ_docs, text_docs,
                 id_operation):

        self.id_company = id_company

        self.id_counterparties = id_counterparties

        self.number_docs = number_docs

        self.date_docs = date_docs

        self.summ_docs = summ_docs

        self.text_docs = text_docs

        self.id_operation = id_operation


class Operations(Base):

    __tablename__ = 'operations'

    id = Column(Integer, primary_key=True)

    name = Column(String(50))

    direction = Column(String(400))

    def __init__(self, name, direction):

        self.name = name

        self.direction = direction


Base.metadata.create_all(engine)
