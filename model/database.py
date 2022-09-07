from sqlalchemy import Column, Date, Enum, ForeignKey, Text, String
from sqlalchemy.dialects.mysql import INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


class Category(Base):
    __tablename__ = 'category'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)
    emoticon = Column(String(45), nullable=True)



class IncomeType(Base):
    __tablename__ = 'income_type'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    name = Column(Text, nullable=False)


class Limit(Base):
    __tablename__ = 'limit'

    id = Column(INTEGER(11), primary_key=True, autoincrement=True)
    day_name = Column(Enum('MONDAY', 'TUESDAY', 'WEDNESDAY', 'THURSDAY', 'FRIDAY', 'SATURDAY', 'SUNDAY'), nullable=False)
    limit_amount = Column(INTEGER(11), nullable=False)


class BudgetPlan(Base):
    __tablename__ = 'budget_plan'

    id = Column(INTEGER(11), primary_key=True, nullable=False, autoincrement=True)
    category_id = Column(ForeignKey('category.id'), primary_key=True, nullable=False, index=True)
    date_buy = Column(Date, nullable=False)
    detail = Column(Text)
    amount = Column(INTEGER(11), nullable=False)

    category = relationship('Category')


class Income(Base):
    __tablename__ = 'income'

    id = Column(INTEGER(11), primary_key=True, nullable=False, autoincrement=True)
    income_type_id = Column(ForeignKey('income_type.id'), primary_key=True, nullable=False, index=True)
    date_created = Column(Date, nullable=False)
    amount = Column(INTEGER(11), nullable=False)
    detail = Column(Text)

    income_type = relationship('IncomeType')


class LimitPlan(Base):
    __tablename__ = 'limit_plan'

    id = Column(INTEGER(11), primary_key=True, nullable=False, autoincrement=True)
    limit_id = Column(ForeignKey('limit.id'), primary_key=True, nullable=False, index=True)
    name = Column(Text, nullable=False)

    limit = relationship('Limit')


class Outcome(Base):
    __tablename__ = 'outcome'

    id = Column(INTEGER(11), primary_key=True, nullable=False, autoincrement=True)
    category_id = Column(ForeignKey('category.id'), primary_key=True, nullable=False, index=True)
    income_type_id = Column(ForeignKey('income_type.id'), primary_key=True, nullable=False, index=True)
    detail_item = Column(Text)
    amount = Column(INTEGER(11), nullable=False)
    date_created = Column(Date, nullable=False)

    category = relationship('Category')
    income_type = relationship('IncomeType')


class SavingPlan(Base):
    __tablename__ = 'saving_plan'

    id = Column(INTEGER(11), primary_key=True, nullable=False, autoincrement=True)
    income_type_id = Column(ForeignKey('income_type.id'), primary_key=True, nullable=False, index=True)
    date_saving = Column(Date, nullable=False)
    amount = Column(INTEGER(11), nullable=False)

    income_type = relationship('IncomeType')