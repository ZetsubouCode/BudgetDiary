from controller.Category import Category as CategoryController
from temp_db import temp_db

class Category:
    async def add(msg):
        '''@param name = the name of the category'''
        data = msg.split("#")
        if len(data)==2:
          name = data[0]
          emot = ":"+data[1]+":"
        elif len(data)==1:
          name = data[0]
          emot = None
        else : 
          return None
        await CategoryController.add(name,emot)
        return True

    async def get_all():
        category = await CategoryController.get_all()
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

    async def get_all_raw():
        return await CategoryController.get_all()