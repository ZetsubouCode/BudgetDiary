from typing import List
from datetime import date
from sqlalchemy.sql import func
from __database import get_session
from model.database import SavingPlan as SavingPlanModel
from utils import Debug, DebugLevel

class SavingPlan:
    @staticmethod
    async def get_by_id(target_id: int) -> SavingPlanModel:
        """
        Get the first result of SavingPlan by its id
        @param target_id: The id of the SavingPlan data
        @return: SavingPlan object
        """
        with get_session() as session:
            saving_plan = session.query(SavingPlanModel).filter_by(id=target_id).first()

        return saving_plan
    
    @staticmethod
    async def get_all() -> List[SavingPlanModel]:
        """
        Get all result of SavingPlan data
        @return: List of SavingPlan object
        """
        with get_session() as session:
            saving_plan = session.query(SavingPlanModel).all()
        return saving_plan

    @staticmethod
    async def get_monthly_saving_plan(first_date:date, last_date:date) -> List[SavingPlanModel]:
        """
        Get all result of SavingPlan data
        @return: List of SavingPlan object
        """
        with get_session() as session:
            saving_plan = session.query(func.sum(SavingPlanModel.amount).label("amount")
            ).filter(SavingPlanModel.date_saving>=first_date,SavingPlanModel.date_saving<=last_date).all()
        return saving_plan

    @staticmethod
    async def get_monthly_total(first_date:date, last_date:date) -> List[SavingPlanModel]:
        """
        Get all result of SavingPlan data
        @return: List of SavingPlan object
        """
        with get_session() as session:
            saving_plan = session.query(func.sum(SavingPlanModel.amount).label("amount")
            ).filter(SavingPlanModel.date_saving>=first_date,SavingPlanModel.date_saving<=last_date).all()
        return saving_plan

    @staticmethod
    async def get_saving_plan() -> List[SavingPlanModel]:
        """
        Get all result of SavingPlan data
        @return: List of SavingPlan object
        """
        with get_session() as session:
            saving_plan = session.query(func.sum(SavingPlanModel.amount).label("amount")).all()
        return saving_plan

    @staticmethod
    async def get_last_saving_plan(data_date:date) -> List[SavingPlanModel]:
        """
        Get all result of SavingPlan data
        @return: List of SavingPlan object
        """
        with get_session() as session:
            saving_plan = session.query(func.sum(SavingPlanModel.amount).label("amount")
            ).filter(SavingPlanModel.date_saving<data_date).all()
        return saving_plan

    @staticmethod
    async def add(income_type_id:int, date_saving:date, amount:int)-> SavingPlanModel:
        """
        Create SavingPlan object and add it to the database
        @param last_layer: SavingPlan last_layer
        @param last_room: SavingPlan last_room
        @return: SavingPlan object
        """
        with get_session() as session:
            saving_plan = SavingPlanModel(income_type_id=income_type_id, amount=amount, date_saving=date_saving)
            session.add(saving_plan)
            session.commit()
            session.flush()
            session.refresh(saving_plan)

            return saving_plan
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:SavingPlanModel) -> SavingPlanModel:
        """
        Update SavingPlan object that have the specific id
        @param taget_id: SavingPlan id
        @param new_obj: SavingPlan SavingPlan new set of data
        @return: SavingPlan object
        """
        with get_session() as sess:
            sess.query(SavingPlanModel).filter_by(id=int(target_id)).update(
                    {
                        SavingPlanModel.income_type_id: new_obj.income_type_id,
                        SavingPlanModel.amount : new_obj.amount,
                        SavingPlanModel.date_saving : new_obj.date_saving,
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete SavingPlan object that have the specific id
        @param taget_id: SavingPlan id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(SavingPlanModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("SavingPlanController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("SavingPlanController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)