import json, os
from temp_db import temp_db
from util.date_utils import Util
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

        # Construct the new data
        template_data = {
            discord_user_id: template_content
        }

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

    async def add(name:str,trans_type:str = "income",emoticon:str=""):
        try:
            trans_type = trans_type.lower()
            json_file = Category.get_categories()
            income_type = json_file.get(trans_type,[])
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
            json_file[trans_type] = income_type

            with open(JSON_CATEGORY_FILE_PATH, 'w') as file:
                json.dump(json_file, file, indent=4)

            temp_db._income_type = income_type
            message = f"Success add {name} {emoticon}"
            Category.logger.log(level=40,message=message)
            return True,message,None
        except Exception as e:
            Category.logger.log(level=1,message=e)
            return False,"Failed to add Category",e

    async def get_all(category_type: str = None):
        try:
            # Read JSON file containing categories
            json_file = Util.read_json(JSON_CATEGORY_FILE_PATH)

            # If category_type is None, get both "income" and "outcome" categories
            if category_type is None:
                categories_data = {}
                for cat_type in ["income", "outcome"]:
                    category = json_file.get(cat_type, [])
                    categories_data[cat_type.title()] = {f"Category {i+1}": f"{data['description']['ENG']} {data.get('emoticon', '')}" 
                                                        for i, data in enumerate(category)}
            else:
                # Get the specified category type (income or outcome)
                category = json_file.get(category_type, [])
                categories_data = {category_type.title(): {f"Category {i+1}": f"{data['description']['ENG']} {data.get('emoticon', '')}" 
                                                            for i, data in enumerate(category)}}

            return True, categories_data  # Return as JSON-like structure
        except Exception as e:
            return False, f"Error: {str(e)}"

    def delete_category(category_type, category_id):
        categories = Category.get_categories(category_type)
        updated_categories = [cat for cat in categories if cat["id"] != category_id]

        if len(categories) == len(updated_categories):
            return f"Category ID {category_id} not found."

        with open(f"{category_type}_categories.json", "w") as file:
            json.dump(updated_categories, file, indent=4)
        return f"Category ID {category_id} deleted successfully!"