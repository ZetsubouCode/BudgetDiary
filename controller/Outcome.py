from typing import List
from sqlalchemy.sql import func
from datetime import date
from sqlalchemy.orm import joinedload
from __database import get_session
from model.database import Outcome as OutcomeModel
from model.database import IncomeType as IncomeTypeModel
from utils import Debug, DebugLevel

class Outcome:
    @staticmethod
    async def get_by_id(target_id: int) -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).filter_by(id=target_id).first()

        return outcome

    @staticmethod
    async def get_outcome() -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(func.sum(OutcomeModel.amount).label("amount")).all()

        return outcome

    @staticmethod
    async def get_last_outcome(data_date:date) -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(func.sum(OutcomeModel.amount).label("amount")
            ).filter(OutcomeModel.date_created<data_date).all()

        return outcome

    
    @staticmethod
    async def get_specific_latest_outcome(keyword:str,category_id:int) -> OutcomeModel:
        """
        Get the first result of Outcome by its category id and depend on the keyword
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).options(joinedload(OutcomeModel.category), joinedload(OutcomeModel.income_type)
            ).filter(OutcomeModel.category_id==category_id,func.lower(OutcomeModel.detail_item.like(keyword))
                ).order_by(OutcomeModel.date_created.desc()).first()

        return outcome
  
    @staticmethod
    async def get_daily_outcome(target_date: date) -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).options(joinedload(OutcomeModel.category), joinedload(OutcomeModel.income_type)
            ).filter_by(date_created=target_date).all()

        return outcome
    
    @staticmethod
    async def get_monthly_outcome(first_date: date, last_date: date) -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).options(joinedload(OutcomeModel.category), joinedload(OutcomeModel.income_type)
            ).filter(OutcomeModel.date_created>=first_date,OutcomeModel.date_created<=last_date).order_by(OutcomeModel.date_created).all()

        return outcome

    @staticmethod
    async def get_group_outcome() -> List[OutcomeModel]:
        """
        Get all result of Outcome data
        @return: List of Outcome object
        """
        with get_session() as session:
            income = session.query(
                func.sum(OutcomeModel.amount).label("amount"),
                IncomeTypeModel.name.label("name")).join(
                    IncomeTypeModel).group_by(
                            IncomeTypeModel.name
            ).order_by(IncomeTypeModel.name).all()
        return income

    @staticmethod
    async def get_monthly_total(first_date: date, last_date: date) -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(func.sum(OutcomeModel.amount).label("amount")).filter(
                OutcomeModel.date_created>=first_date,OutcomeModel.date_created<=last_date).all()

        return outcome
    
    @staticmethod
    async def get_all() -> List[OutcomeModel]:
        """
        Get all result of Outcome data
        @return: List of Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).all()
        return outcome

    @staticmethod
    async def add(category_id: int, income_type_id:int, detail_item:str, amount:int, date_created:date) -> OutcomeModel:
        """
        Create Outcome object and add it to the database
        @param last_layer: Outcome last_layer
        @param last_room: Outcome last_room
        @return: Outcome object
        """
        with get_session() as session:
            outcome = OutcomeModel(category_id=category_id, income_type_id=income_type_id,date_created=date_created, detail_item=detail_item, amount=amount)
            session.add(outcome)
            session.commit()
            session.flush()
            session.refresh(outcome)

            return outcome
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:OutcomeModel) -> OutcomeModel:
        """
        Update Outcome object that have the specific id
        @param taget_id: Outcome id
        @param new_obj: Outcome Outcome new set of data
        @return: Outcome object
        """
        with get_session() as sess:
            sess.query(OutcomeModel).filter_by(id=int(target_id)).update(
                    {
                        OutcomeModel.category_id: new_obj.category_id,
                        OutcomeModel.income_type_id: new_obj.income_type_id,
                        
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete Outcome object that have the specific id
        @param taget_id: Outcome id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(OutcomeModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("OutcomeController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("OutcomeController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)
