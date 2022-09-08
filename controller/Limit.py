from typing import List
from __database import get_session
from model.database import Limit as LimitModel
from utils import Debug, DebugLevel

class Limit:
    @staticmethod
    async def get_by_id(target_id: int) -> LimitModel:
        """
        Get the first result of Limit by its id
        @param target_id: The id of the Limit data
        @return: Limit object
        """
        with get_session() as session:
            limit = session.query(LimitModel).filter_by(id=target_id).first()

        return limit
    
    @staticmethod
    async def get_all() -> List[LimitModel]:
        """
        Get all result of Limit data
        @return: List of Limit object
        """
        with get_session() as session:
            limit = session.query(LimitModel).all()
        return limit

    @staticmethod
    async def add(day_name:str,limit_amount:int)-> LimitModel:
        """
        Create Limit object and add it to the database
        @param last_layer: Limit last_layer
        @param last_room: Limit last_room
        @return: Limit object
        """
        with get_session() as session:
            limit = LimitModel(day_name=day_name, limit_amount=limit_amount)
            session.add(limit)
            session.commit()
            session.flush()
            session.refresh(limit)

            return limit
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:LimitModel) -> LimitModel:
        """
        Update Limit object that have the specific id
        @param taget_id: Limit id
        @param new_obj: Limit Limit new set of data
        @return: Limit object
        """
        with get_session() as sess:
            sess.query(LimitModel).filter_by(id=int(target_id)).update(
                    {
                        LimitModel.day_name: new_obj.day_name,
                        LimitModel.limit_amount: new_obj.limit_amount
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete Limit object that have the specific id
        @param taget_id: Limit id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(LimitModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("LimitController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("LimitController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)