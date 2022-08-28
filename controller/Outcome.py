from typing import List, Optional
from datetime import date
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
    async def get_all() -> List[OutcomeModel]:
        """
        Get all result of Outcome data
        @return: List of Outcome object
        """
        with get_session() as session:
            outcome = session.query(OutcomeModel).all()
        return outcome

    @staticmethod
    async def add(last_layer:int, last_room:int)-> OutcomeModel:
        """
        Create Outcome object and add it to the database
        @param last_layer: Outcome last_layer
        @param last_room: Outcome last_room
        @return: Outcome object
        """
        with get_session() as session:
            outcome = OutcomeModel(last_layer=last_layer, last_room=last_room)
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