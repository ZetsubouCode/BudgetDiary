from typing import List
from __database import get_session
from model.database import IncomeType as IncomeTypeModel
from utils import Debug, DebugLevel

class IncomeType:
    @staticmethod
    async def get_by_id(target_id: int) -> IncomeTypeModel:
        """
        Get the first result of IncomeType by its id
        @param target_id: The id of the IncomeType data
        @return: IncomeType object
        """
        with get_session() as session:
            income_type = session.query(IncomeTypeModel).filter_by(id=target_id).first()

        return income_type
    
    @staticmethod
    async def get_all() -> List[IncomeTypeModel]:
        """
        Get all result of IncomeType data
        @return: List of IncomeType object
        """
        with get_session() as session:
            income_type = session.query(IncomeTypeModel).all()
        return income_type

    @staticmethod
    async def add(name:str)-> IncomeTypeModel:
        """
        Create IncomeType object and add it to the database
        @param last_layer: IncomeType last_layer
        @param last_room: IncomeType last_room
        @return: IncomeType object
        """
        with get_session() as session:
            income_type = IncomeTypeModel(name=name)
            session.add(income_type)
            session.commit()
            session.flush()
            session.refresh(income_type)

            return income_type
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:IncomeTypeModel) -> IncomeTypeModel:
        """
        Update IncomeType object that have the specific id
        @param taget_id: IncomeType id
        @param new_obj: IncomeType IncomeType new set of data
        @return: IncomeType object
        """
        with get_session() as sess:
            sess.query(IncomeTypeModel).filter_by(id=int(target_id)).update(
                    {
                        IncomeTypeModel.name: new_obj.name,
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete IncomeType object that have the specific id
        @param taget_id: IncomeType id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(IncomeTypeModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("IncomeTypeController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("IncomeTypeController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)