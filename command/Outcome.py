import json
from datetime import timedelta, date, datetime
from config.config import *
from util.date_utils import Util
from util.logger import LoggerSingleton


class Outcome:
    logger = LoggerSingleton.get_instance()
    async def add(discord_id:str,outcome_type:str,amount:int,detail:str,date:str):
        year,month,day = date.split("-")
        
        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        # If file is empty, initialize with template
        if not json_file:
            json_template = Util.read_json(JSON_TRANSACTION_TEMPLATE_FILE_PATH)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(json_template, file, indent=4)

        # Reload json file after potential creation
        json_file = Util.read_json(file_path)

        # Get latest index and increment
        latest_id = max(map(int, json_file["outcome"]["by_id"].keys()), default=0)
        index = str(latest_id + 1)

        # Ensure date is in string format
        date_now = datetime.now().isoformat()

        # Insert new outcome entry
        transaction = {
            "category_id": outcome_type,
            "description": detail,
            "amount": amount,
            "date": date,
            "date_created": date_now,
            "is_deleted": False,
            "deleted_at": None
        }
        json_file["outcome"]["by_id"][index] = transaction

        # Ensure date hierarchy exists
        json_file["outcome"]["by_date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, [])
        json_file["outcome"]["by_date"][year][month][day].append(index)
        
        # Ensure by_category exists as a list
        json_file["outcome"]["by_category"].setdefault(outcome_type, [])
        json_file["outcome"]["by_category"][outcome_type].append(index)
        
        json_file = Outcome.update_summary(json_file,transaction,"add","outcome")
        # Write back to file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_file, file, indent=4)

        message = f"Success add Rp {amount} to balance"
        Outcome.logger.log(level=40,message=message)
        return True,message,None