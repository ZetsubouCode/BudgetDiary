from typing import List
from datetime import date
from sqlalchemy.sql import func
from __database import get_session
from model.database import LimitPlan as LimitPlanModel
from utils import Debug, DebugLevel

class LimitPlan:
    @staticmethod
    async def get_by_id(target_id: int) -> LimitPlanModel:
        """
        Get the first result of LimitPlan by its id
        @param target_id: The id of the LimitPlan data
        @return: LimitPlan object
        """
        with get_session() as session:
            limit_plan = session.query(LimitPlanModel).filter_by(id=target_id).first()

        return limit_plan
    
    @staticmethod
    async def get_all() -> List[LimitPlanModel]:
        """
        Get all result of LimitPlan data
        @return: List of LimitPlan object
        """
        with get_session() as session:
            limit_plan = session.query(LimitPlanModel).all()
        return limit_plan

    @staticmethod
    async def add(limit_id:int, name:str)-> LimitPlanModel:
        """
        Create LimitPlan object and add it to the database
        @param last_layer: LimitPlan last_layer
        @param last_room: LimitPlan last_room
        @return: LimitPlan object
        """
        with get_session() as session:
            limit_plan = LimitPlanModel(limit_id=limit_id, name=name)
            session.add(limit_plan)
            session.commit()
            session.flush()
            session.refresh(limit_plan)

            return limit_plan
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:LimitPlanModel) -> LimitPlanModel:
        """
        Update LimitPlan object that have the specific id
        @param taget_id: LimitPlan id
        @param new_obj: LimitPlan LimitPlan new set of data
        @return: LimitPlan object
        """
        with get_session() as sess:
            sess.query(LimitPlanModel).filter_by(id=int(target_id)).update(
                    {
                        LimitPlanModel.limit_id: new_obj.limit_id,
                        LimitPlanModel.name : new_obj.name
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete LimitPlan object that have the specific id
        @param taget_id: LimitPlan id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(LimitPlanModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("LimitPlanController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("LimitPlanController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)