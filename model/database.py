from sqlalchemy import Column, Date, DateTime, Enum, ForeignKey, Text, text
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Category(Base):
    __tablename__ = 'category'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)


class Transaction(Base):
    __tablename__ = 'transaction'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    total = Column(INTEGER(11))
    date_transaction = Column(Date)


class Income(Base):
    __tablename__ = 'income'

    id = Column(INTEGER(11), primary_key=True, nullable=False, autoincrement=True)
    transaction_id = Column(ForeignKey('transaction.id'), primary_key=True, nullable=False, index=True)
    date_created = Column(Date, nullable=False, server_default=text("curdate()"))
    amount = Column(INTEGER(11), nullable=False)
    type = Column(Enum('BANK BCA', 'BANK ALADIN', 'GIFT', 'CASH', 'GOPAY', 'OVO', 'SHOPEE PAY'), nullable=False)
    detail = Column(Text)

    transaction = relationship('Transaction')


class Outcome(Base):
    __tablename__ = 'outcome'

    id = Column(INTEGER(11), primary_key=True, nullable=False, autoincrement=True)
    category_id = Column(ForeignKey('category.id'), primary_key=True, nullable=False, index=True)
    transaction_id = Column(ForeignKey('transaction.id'), index=True)
    detail_item = Column(Text)
    amount = Column(INTEGER(11), nullable=False)
    date_created = Column(DateTime, nullable=False, server_default=text("curdate()"))

    category = relationship('Category')
    transaction = relationship('Transaction')