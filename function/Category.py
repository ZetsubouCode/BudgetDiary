import json
from temp_db import temp_db
from utils import Util

class Category:
    JSON_FILE_PATH = "data/category.json"

    async def add(name, emoticon,type):
        try:
            json_file = Util.read_json(Category.JSON_FILE_PATH)
            income_type = json_file.get(type,[])
            latest_data = income_type[-1]
            new_data = {
                "id":int(latest_data.get("id",0))+1,
                "description":{
                    "INA":name,
                    "ENG":name
                },
                "emoticon":emoticon
            }
            income_type.append(new_data)
             # Update the json_file with the modified income_type list
            json_file[type] = income_type

            with open(Category.JSON_FILE_PATH, 'w') as file:
                json.dump(json_file, file, indent=4)

            temp_db._income_type = income_type
            return True
        except Exception as e:
            print(e)
            return None


    async def get_all():
        json_file = Util.read_json(Category.JSON_FILE_PATH)
        category = json_file.get("income",[])
        message = "**LIST CATEGORY\n**"
        for data in category:
            if data.get("emoticon",None) is None:
                emot = ""
            else :
                emot = data.emoticon+" "
            message += f"{data['id']}. {emot}{data['name']}\n"
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

    def get_all_raw():
        return CategoryController.get_all()