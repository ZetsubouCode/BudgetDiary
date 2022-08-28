from typing import List, Optional
from datetime import date
from __database import get_session
from model.database import Transaction as TransactionModel
from utils import Debug, DebugLevel

class Transaction:
    @staticmethod
    async def get_by_id(target_id: int) -> TransactionModel:
        """
        Get the first result of Transaction by its id
        @param target_id: The id of the Transaction data
        @return: Transaction object
        """
        with get_session() as session:
            transaction = session.query(TransactionModel).filter_by(id=target_id).first()

        return transaction
    
    @staticmethod
    async def get_all() -> List[TransactionModel]:
        """
        Get all result of Transaction data
        @return: List of Transaction object
        """
        with get_session() as session:
            transaction = session.query(TransactionModel).all()
        return transaction

    @staticmethod
    async def add(last_layer:int, last_room:int)-> TransactionModel:
        """
        Create Transaction object and add it to the database
        @param last_layer: Transaction last_layer
        @param last_room: Transaction last_room
        @return: Transaction object
        """
        with get_session() as session:
            transaction = TransactionModel(last_layer=last_layer, last_room=last_room)
            session.add(transaction)
            session.commit()
            session.flush()
            session.refresh(transaction)

            return transaction
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:TransactionModel) -> TransactionModel:
        """
        Update Transaction object that have the specific id
        @param taget_id: Transaction id
        @param new_obj: Transaction Transaction new set of data
        @return: Transaction object
        """
        with get_session() as sess:
            sess.query(TransactionModel).filter_by(id=int(target_id)).update(
                    {
                        TransactionModel.last_layer : new_obj.last_layer,
                        TransactionModel.last_room : new_obj.last_room,
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete Transaction object that have the specific id
        @param taget_id: Transaction id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(TransactionModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("TransactionController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("TransactionController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)