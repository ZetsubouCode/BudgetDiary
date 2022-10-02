from typing import List
from datetime import date
from sqlalchemy.sql import func
from sqlalchemy.orm import joinedload
from __database import get_session
from model.database import Income as IncomeModel
from model.database import IncomeType as IncomeTypeModel
from utils import Debug, DebugLevel

class Income:
    @staticmethod
    async def get_by_id(target_id: int) -> IncomeModel:
        """
        Get the first result of Income by its id
        @param target_id: The id of the Income data
        @return: Income object
        """
        with get_session() as session:
            income = session.query(IncomeModel).filter_by(id=target_id).first()

        return income

    @staticmethod
    async def get_by_income_type_and_date(income_type_id: int,
                                          first_date: date,
                                          last_date: date) -> IncomeModel:
        """
        Get the first result of Income by its id
        @param target_id: The id of the Income data
        @return: Income object
        """
        with get_session() as session:
            income = session.query(IncomeModel).filter(
                IncomeModel.income_type_id == income_type_id,
                IncomeModel.date_created >= first_date,
                IncomeModel.date_created <= last_date).all()

        return income

    @staticmethod
    async def get_all() -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(IncomeModel).options(
                joinedload(IncomeModel.income_type)).all()
        return income
        
    @staticmethod
    async def get_daily_income(date:date) -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(IncomeModel).options(
                joinedload(IncomeModel.income_type)
                ).filter(IncomeModel.date_created == date).all()
        return income

    @staticmethod
    async def get_monthly_income(first_date: date,
                                 last_date: date) -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(IncomeModel).options(
                joinedload(IncomeModel.income_type)).filter(
                    IncomeModel.date_created >= first_date,
                    IncomeModel.date_created <= last_date,
                    IncomeModel.amount > 0).order_by(
                        IncomeModel.date_created).all()
        return income

    @staticmethod
    async def get_group_income() -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(
                func.sum(IncomeModel.amount).label("amount"),
                IncomeTypeModel.name.label("name")).join(
                    IncomeTypeModel).group_by(
                            IncomeTypeModel.name
            ).order_by(IncomeTypeModel.name).all()
        return income

    @staticmethod
    async def get_this_month_income(first_date: date,
                                    last_date: date) -> List[IncomeModel]:
        """
        Get sum result of Income data
        @return: int value of the sum result
        """
        with get_session() as session:
            income = session.query(
                func.sum(IncomeModel.amount).label("amount")).filter(
                    IncomeModel.date_created >= first_date,
                    IncomeModel.date_created <= last_date).all()
        return income

    @staticmethod
    async def get_last_income(data_date: date) -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(
                func.sum(IncomeModel.amount).label("amount")).filter(
                    IncomeModel.date_created < data_date).all()
        return income

    @staticmethod
    async def add(amount: int, date_created: date, income_type_id: int,
                  detail: str) -> IncomeModel:
        """
        Create Income object and add it to the database
        @param last_layer: Income last_layer
        @param last_room: Income last_room
        @return: Income object
        """
        with get_session() as session:
            income = IncomeModel(amount=amount,
                                 date_created=date_created,
                                 income_type_id=income_type_id,
                                 detail=detail)
            session.add(income)
            session.commit()
            session.flush()
            session.refresh(income)

            return income

    @staticmethod
    async def update_by_id(target_id: int,
                           new_obj: IncomeModel) -> IncomeModel:
        """
        Update Income object that have the specific id
        @param taget_id: Income id
        @param new_obj: Income Income new set of data
        @return: Income object
        """
        with get_session() as sess:
            sess.query(IncomeModel).filter_by(id=int(target_id)).update({
                IncomeModel.income_type_id:
                new_obj.income_type_id,
                IncomeModel.date_created:
                new_obj.date_created,
                IncomeModel.amount:
                new_obj.amount,
                IncomeModel.detail:
                new_obj.detail,
            })
            sess.commit()
        return new_obj

    @staticmethod
    async def reduce_amount_by_id(target_id: int, amount: int) -> IncomeModel:
        """
        Update Income object that have the specific id
        @param taget_id: Income id
        @param new_obj: Income Income new set of data
        @return: Income object
        """
        with get_session() as sess:
            sess.query(IncomeModel).filter_by(id=int(target_id)).update(
                {IncomeModel.amount: IncomeModel.amount - amount})
            data = sess.commit()
        return data

    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete Income object that have the specific id
        @param taget_id: Income id
        """
        try:
            with get_session() as sess:

                try:
                    sess.query(IncomeModel).filter_by(
                        id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()

                except Exception as e:
                    sess.rollback()
                    Debug.msg("IncomeController|delete_by_id",
                              "Failed to Delete {}".format(e),
                              DebugLevel.WARNING)

        except Exception as e:
            Debug.msg("IncomeController|delete_by_id",
                      "Exception Raised {}".format(e), DebugLevel.ERROR)
