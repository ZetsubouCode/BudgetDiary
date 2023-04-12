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

    async def get_all():
        category = await get_all_raw()
        message = "**LIST CATEGORY\n**"
        for data in category:
            if data.emoticon is None:
                emot = ""
            else :
                emot = data.emoticon+" "
            message += f"{data.id}. {emot}{data.name}\n"
        return message

    async def get_all_temp():
        category = temp_db._category
        message = "**LIST CATEGORY\n**"
        print(category)
        for data in category:
            print(data)
            if data.emoticon is None:
                emot = ""
            else :
                emot = data.emoticon+" "
            message += f"{data.id}. {emot}{data.name}\n"
        return message
