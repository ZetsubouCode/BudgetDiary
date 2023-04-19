from controller.Category import Category as CategoryController
from temp_db import temp_db
from util import Util

class Category:
    main_endpoint = "category"
    
    async def add(name, emot):
        form_data = {
        "name":name,
         "emoticon":emot
        }
        sub_endpoint = "add"
        category = Util.send_request('POST',main_endpoint,sub_endpoint,data=form_data)
        return True

    async def get_all_raw():
        sub_endpoint = "all"
        category = Util.send_request('GET',main_endpoint,sub_endpoint)
        return category 

    async def get_all(raw_option:bool=False):
        try:
            if raw_option :
                category = await get_all_raw()
            else:
                category = temp_db._category
            message = "**LIST CATEGORY\n**"
            for idx,data in enumerate(category):
                emot = (data.emoticon or "")+" "
                message += f"{(idx+1)}. {emot}{data.name}\n"
            return message
        except Exception as e:
            # Handle the exception here
            print(f"Error: {e}")
            return "An error occurred while retrieving category data."
