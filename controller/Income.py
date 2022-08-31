from typing import List, Optional
from datetime import date
from sqlalchemy.sql import func
from __database import get_session
from model.database import Income as IncomeModel
from utils import Debug, DebugLevel
from model.enum import IncomeType

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
    async def get_all() -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(IncomeModel).all()
        return income

    @staticmethod
    async def get_this_month_saving(first_date:date, last_date:date) -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(func.sum(IncomeModel.amount).label("amount")
            ).filter(IncomeModel.date_created>=first_date,IncomeModel.date_created<=last_date).all()
        return income

    @staticmethod
    async def get_saving() -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(func.sum(IncomeModel.amount).label("amount")).all()
        return income

    @staticmethod
    async def get_last_saving(data_date:date) -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(func.sum(IncomeModel.amount).label("amount")
            ).filter(IncomeModel.date_created<data_date).all()
        return income

    @staticmethod
    async def add(transaction_id:int, amount:int, type:IncomeType, detail:str)-> IncomeModel:
        """
        Create Income object and add it to the database
        @param last_layer: Income last_layer
        @param last_room: Income last_room
        @return: Income object
        """
        with get_session() as session:
            income = IncomeModel(transaction_id=transaction_id, amount=amount, type=type, detail=detail)
            session.add(income)
            session.commit()
            session.flush()
            session.refresh(income)

            return income
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:IncomeModel) -> IncomeModel:
        """
        Update Income object that have the specific id
        @param taget_id: Income id
        @param new_obj: Income Income new set of data
        @return: Income object
        """
        with get_session() as sess:
            sess.query(IncomeModel).filter_by(id=int(target_id)).update(
                    {
                        IncomeModel.transaction_id : new_obj.transaction_id,
                        IncomeModel.amount : new_obj.amount,
                        IncomeModel.type : new_obj.type,
                        IncomeModel.detail : new_obj.detail,
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete Income object that have the specific id
        @param taget_id: Income id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(IncomeModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("IncomeController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("IncomeController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)