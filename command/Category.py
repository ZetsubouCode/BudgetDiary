import json, os
from util.date_utils import Util
from util.text_handler import TextHandler
from util.data_handler import DataHandler
from util.logger import LoggerSingleton
from config.config import *


class Category:

    logger = LoggerSingleton.get_instance()
    def get_categories(category_type=""):
        file_path = JSON_CATEGORY_FILE_PATH
        try:
            with open(file_path, "r") as file:
                if category_type=="":
                    return json.load(file)
                else:
                    return json.load(file).get(category_type,{})
        except FileNotFoundError:
            return []
    
    def append_template_to_json(discord_user_id: str, discord_username=""):
        """
        Appends a template dictionary for a specific Discord user ID into a target JSON file.

        Args:
            discord_user_id (str): The Discord user ID to be added.
            discord_username (str): Optional username for the Discord user.

        Returns:
            tuple: (bool, str) - Status and success/error message.
        """
        # Load the template file
        try:
            with open(JSON_CATEGORY_TEMPLATE_FILE_PATH, "r") as file:
                template_content = json.load(file)
        except FileNotFoundError:
            return False, "Error: Template JSON file not found."
        except json.JSONDecodeError:
            return False, "Error: Template JSON file is not valid."

        # # Construct the new data
        # template_data = {
        #     discord_user_id: template_content
        # }

        # Ensure the target JSON file exists
        if not os.path.exists(JSON_CATEGORY_FILE_PATH):
            with open(JSON_CATEGORY_FILE_PATH, "w") as file:
                json.dump({}, file)  # Create an empty JSON object

        # Load the target JSON file
        try:
            with open(JSON_CATEGORY_FILE_PATH, "r") as file:
                existing_data = json.load(file)
        except FileNotFoundError:
            return False, "Error: Target JSON file not found."
        except json.JSONDecodeError:
            return False, "Error: Target JSON file is not valid."

        # Debugging: Print existing keys
        print(f"Discord User ID: {discord_user_id}")
        print(f"Existing Keys: {list(existing_data.keys())}")

        # Check if the user ID already exists
        if str(discord_user_id) in existing_data:
            return False, f"User {discord_username} already has category."

        # Add the new data
        existing_data[discord_user_id] = template_content

        # Save the updated data back to the JSON file
        try:
            with open(JSON_CATEGORY_FILE_PATH, "w") as file:
                json.dump(existing_data, file, indent=4)
            return True, f"Template for User {discord_username} added successfully."
        except IOError as e:
            return False, f"Error: Unable to write to the target JSON file. {e}"

    async def add(discord_id:str,name:str,trans_type:str = "income",emoticon:str=""):
        try:
            trans_type = trans_type.lower()
            json_file = Util.read_json(JSON_CATEGORY_FILE_PATH)
            
            list_data = json_file.get(discord_id,{}).get(trans_type,{})
            latest_key = list(list_data.keys())[-1]
            
            new_idx = str(int(latest_key)+1)
            list_data[new_idx] = {
                    "description":{
                        "id":name,
                        "en":name
                    },
                    "emoticon":emoticon
                }
             # Update the json_file with the modified list_data list
            json_file[discord_id][trans_type] = list_data

            with open(JSON_CATEGORY_FILE_PATH, 'w') as file:
                json.dump(json_file, file, indent=4)

            message = f"Success add {name} {emoticon}"
            Category.logger.log(level=40,message=message)
            return True,message,None
        except Exception as e:
            Category.logger.log(level=1,message=e)
            return False,"Failed to add Category",e
        
    async def edit(discord_id:str,category_id:str,new_name:str,emoticon:str,trans_type:str = "outcome",language="en"):
        try:
            trans_type = trans_type.lower()
            json_file = Util.read_json(JSON_CATEGORY_FILE_PATH)
            
            income_type = json_file.get(discord_id,{}).get(trans_type,[])
            selected_data = income_type[category_id]
            
            selected_data["description"][language] = new_name
            if emoticon != "":
                selected_data["emoticon"] = emoticon
            
            income_type[category_id] = selected_data
             # Update the json_file with the modified income_type list
            json_file[discord_id][trans_type] = income_type

            with open(JSON_CATEGORY_FILE_PATH, 'w') as file:
                json.dump(json_file, file, indent=4)

            message = f"Success edit data into {new_name} {emoticon}"
            Category.logger.log(level=40,message=message)
            return True,message,None
        except Exception as e:
            Category.logger.log(level=1,message=e)
            return False,"Failed to edit Category",e

    async def get_all(discord_id:str,category_type: str = None, raw_data: bool = False):
        try:
            # Read JSON file containing categories
            json_file = Util.read_json(JSON_CATEGORY_FILE_PATH).get(discord_id,{})
            user_json_file = Util.read_json(JSON_USER_FILE_PATH).get(discord_id,{})
            language = user_json_file.get('language',"en")
            # If category_type is None, get both "income" and "outcome" categories
            if raw_data:
                filtered_data = {
                    k: v for k, v in json_file.get(category_type, {}).items() if not v.get("is_deleted", False)
                }
                return True, "Success", filtered_data
            
            if category_type is None:
                categories_data = {}
                for cat_type in ["income", "outcome"]:
                    category = json_file.get(cat_type, {})
                    category = DataHandler.dict_to_list(category)
                    categories_data[cat_type.title()] = {f"Category {i+1}": f"{data['description'][language]} {data.get('emoticon', '')}" 
                                                        for i, data in enumerate(category) if not data.get("is_deleted", False)}
            else:
                # Get the specified category type (income or outcome)
                category = json_file.get(category_type, {})
                category = DataHandler.dict_to_list(category)
                categories_data = {category_type.title(): {f"Category {i+1}": f"{data['description'][language]} {data.get('emoticon', '')}" 
                                                            for i, data in enumerate(category) if not data.get("is_deleted", False)}}

            return True, "Success",categories_data  # Return as JSON-like structure
        except Exception as e:
            return False, f"Error: {str(e)}", None

    async def delete(discord_id:str,category_type:str, category_id:str):
        json_file = Util.read_json(JSON_CATEGORY_FILE_PATH)
        
        categories = json_file.get(discord_id,{}).get(category_type,{})
        print(categories)
        if categories == {}:
            return False,f"Category not found in database.",None
        
        categories[category_id]["is_deleted"] = True
        json_file[discord_id][category_type] = categories

        with open(JSON_CATEGORY_FILE_PATH, "w") as file:
            json.dump(json_file, file, indent=4)
        return True,f"Category deleted successfully!",None