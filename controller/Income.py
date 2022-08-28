from typing import List, Optional
from datetime import date
from __database import get_session
from model.database import Income as IncomeModel
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
    async def get_all() -> List[IncomeModel]:
        """
        Get all result of Income data
        @return: List of Income object
        """
        with get_session() as session:
            income = session.query(IncomeModel).all()
        return income

    @staticmethod
    async def add(last_layer:int, last_room:int)-> IncomeModel:
        """
        Create Income object and add it to the database
        @param last_layer: Income last_layer
        @param last_room: Income last_room
        @return: Income object
        """
        with get_session() as session:
            income = IncomeModel(last_layer=last_layer, last_room=last_room)
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
                        IncomeModel.last_layer : new_obj.last_layer,
                        IncomeModel.last_room : new_obj.last_room,
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