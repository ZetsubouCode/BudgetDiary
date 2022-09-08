from typing import List
from sqlalchemy.sql import func
from datetime import date
from sqlalchemy.orm import joinedload
from __database import get_session
from model.database import BudgetPlan as BudgetPlanModel
from utils import Debug, DebugLevel

class BudgetPlan:

    @staticmethod
    async def get_budget_plan_total() -> BudgetPlanModel:
        """
        Get the first result of BudgetPlan by its id
        @param target_id: The id of the BudgetPlan data
        @return: BudgetPlan object
        """
        with get_session() as session:
            budget_plan = session.query(func.sum(BudgetPlanModel.amount).label("amount")).all()

        return budget_plan
    
    @staticmethod
    async def get_monthly_budget_plan(first_date: date, last_date: date) -> BudgetPlanModel:
        """
        Get the first result of BudgetPlan by its id
        @param target_id: The id of the BudgetPlan data
        @return: BudgetPlan object
        """
        with get_session() as session:
            budget_plan = session.query(BudgetPlanModel).options(joinedload(BudgetPlanModel.category)
            ).filter(BudgetPlanModel.date_buy>=first_date,BudgetPlanModel.date_buy<=last_date).all()

        return budget_plan

    @staticmethod
    async def get_monthly_total(first_date: date, last_date: date) -> BudgetPlanModel:
        """
        Get the first result of BudgetPlan by its id
        @param target_id: The id of the BudgetPlan data
        @return: BudgetPlan object
        """
        with get_session() as session:
            budget_plan = session.query(func.sum(BudgetPlanModel.amount).label("amount")).filter(
                BudgetPlanModel.date_buy>=first_date,BudgetPlanModel.date_buy<=last_date).all()

        return budget_plan
    
    @staticmethod
    async def get_all() -> List[BudgetPlanModel]:
        """
        Get all result of BudgetPlan data
        @return: List of BudgetPlan object
        """
        with get_session() as session:
            budget_plan = session.query(BudgetPlanModel).all()
        return budget_plan

    @staticmethod
    async def add(category_id: int, date_buy: date, detail:str, amount:int) -> BudgetPlanModel:
        """
        Create BudgetPlan object and add it to the database
        @param last_layer: BudgetPlan last_layer
        @param last_room: BudgetPlan last_room
        @return: BudgetPlan object
        """
        with get_session() as session:
            budget_plan = BudgetPlanModel(category_id=category_id, date_buy=date_buy, detail=detail, amount=amount)
            session.add(budget_plan)
            session.commit()
            session.flush()
            session.refresh(budget_plan)

            return budget_plan
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:BudgetPlanModel) -> BudgetPlanModel:
        """
        Update BudgetPlan object that have the specific id
        @param taget_id: BudgetPlan id
        @param new_obj: BudgetPlan BudgetPlan new set of data
        @return: BudgetPlan object
        """
        with get_session() as sess:
            sess.query(BudgetPlanModel).filter_by(id=int(target_id)).update(
                    {
                        BudgetPlanModel.category_id : new_obj.category_id,
                        BudgetPlanModel.detail : new_obj.detail,
                        BudgetPlanModel.amount : new_obj.amount,
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete BudgetPlan object that have the specific id
        @param taget_id: BudgetPlan id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(BudgetPlanModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("BudgetPlanController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("BudgetPlanController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)