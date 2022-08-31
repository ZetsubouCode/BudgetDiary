from typing import List, Optional
from sqlalchemy.sql import func
from datetime import date
from sqlalchemy.orm import joinedload
from __database import get_session
from model.database import Outcome as OutcomeModel
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
    async def get_expense() -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(func.sum(OutcomeModel.amount).label("amount")).all()

        return outcome

    @staticmethod
    async def get_last_expense(data_date:date) -> OutcomeModel:
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
    async def get_daily_expense(target_date: date) -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).options(joinedload(OutcomeModel.category)
            ).filter_by(date_created=target_date).all()

        return outcome
    
    @staticmethod
    async def get_monthly_expense(first_date: date, last_date: date) -> OutcomeModel:
        """
        Get the first result of Outcome by its id
        @param target_id: The id of the Outcome data
        @return: Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).options(joinedload(OutcomeModel.category)
            ).filter(OutcomeModel.date_created>=first_date,OutcomeModel.date_created<=last_date).all()

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
    async def add(category_id: int, transaction_id: int, detail_item:int, amount:int) -> OutcomeModel:
        """
        Create Outcome object and add it to the database
        @param last_layer: Outcome last_layer
        @param last_room: Outcome last_room
        @return: Outcome object
        """
        with get_session() as session:
            outcome = OutcomeModel(category_id=category_id, transaction_id=transaction_id, detail_item=detail_item, amount=amount)
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
                        OutcomeModel.last_layer : new_obj.last_layer,
                        OutcomeModel.last_room : new_obj.last_room,
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