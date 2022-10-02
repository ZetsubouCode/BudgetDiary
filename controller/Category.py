from typing import List
from __database import get_session
from model.database import Category as CategoryModel
from utils import Debug, DebugLevel

class Category:
    @staticmethod
    async def get_by_id(target_id: int) -> CategoryModel:
        """
        Get the first result of Category by its id
        @param target_id: The id of the Category data
        @return: Category object
        """
        with get_session() as session:
            category = session.query(CategoryModel).filter_by(id=target_id).first()

        return category
    
    @staticmethod
    def get_all() -> List[CategoryModel]:
        """
        Get all result of Category data
        @return: List of Category object
        """
        with get_session() as session:
            category = session.query(CategoryModel).all()
        return category

    @staticmethod
    async def add(name:str,emoticon:str)-> CategoryModel:
        """
        Create Category object and add it to the database
        @param last_layer: Category last_layer
        @param last_room: Category last_room
        @return: Category object
        """
        with get_session() as session:
            category = CategoryModel(name=name,emoticon=emoticon)
            session.add(category)
            session.commit()
            session.flush()
            session.refresh(category)

            return category
    
    @staticmethod
    async def update_by_id(target_id: int, new_obj:CategoryModel) -> CategoryModel:
        """
        Update Category object that have the specific id
        @param taget_id: Category id
        @param new_obj: Category Category new set of data
        @return: Category object
        """
        with get_session() as sess:
            sess.query(CategoryModel).filter_by(id=int(target_id)).update(
                    {
                        CategoryModel.name: new_obj.name,
                    }
                )
            sess.commit()
        return new_obj
   
    @staticmethod
    async def delete_by_id(target_id: int):
        """
        Delete Category object that have the specific id
        @param taget_id: Category id
        """
        try:
            with get_session() as sess:
            
                try:
                    sess.query(CategoryModel).filter_by(id=int(target_id)).delete()
                    sess.commit()
                    sess.flush()
                    
                except Exception as e:
                    sess.rollback()
                    Debug.msg("CategoryController|delete_by_id", "Failed to Delete {}".format(e), DebugLevel.WARNING)
                    
        except Exception as e:
            Debug.msg("CategoryController|delete_by_id", "Exception Raised {}".format(e), DebugLevel.ERROR)