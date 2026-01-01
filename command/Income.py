from config.config import *
from datetime import date, datetime, timedelta
import json, os
from util.date_utils import Util
from typing import List
from util.logger import LoggerSingleton
from .User import User


class Income:
    logger = LoggerSingleton.get_instance()
    
    def get_transactions_list(by_date: dict, year: str, month: str = None):
        """
        Retrieves all transaction IDs for a given year or month.

        Parameters:
        - by_date (dict): The dictionary containing transactions grouped by date.
        - year (str): The year as a string (e.g., "2024").
        - month (str, optional): The month as a string (e.g., "12" for December).
        If None, returns all transactions for the entire year.

        Returns:
        - list: A list of transaction IDs for the given year or month.
        """

        transactions = []

        # Check if the year exists in the dictionary
        if year in by_date:
            if month:
                # Retrieve transactions for a specific month
                if month in by_date[year]:
                    for day_transactions in by_date[year][month].values():
                        transactions.extend(day_transactions)
            else:
                # Retrieve all transactions for the entire year
                for month_data in by_date[year].values():
                    for day_transactions in month_data.values():
                        transactions.extend(day_transactions)

        return transactions

    def update_summary(summary_data: dict, transaction: dict, action: str, transaction_type: str):
        """
        Updates the summary data when a transaction is added, deleted, or edited.

        Parameters:
        - summary_data (dict): The existing summary JSON structure.
        - transaction (dict): The transaction data (must include amount, category_id, type, and date).
        - action (str): The action type ('add', 'delete', 'edit').
        - transaction_type (str): Either 'income' or 'outcome'.

        Returns:
        - dict: Updated summary data.
        """

        # Extract transaction details
        amount = transaction["amount"]
        category_id = str(transaction["category_id"])
        date_str = transaction["date"]
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")

        year = str(date_obj.year)
        month = str(date_obj.month)

        # Ensure year and month exist in summary
        summary_data.setdefault(year, {"summary": {}, month: {}})
        summary_data[year].setdefault(month, {})

        # Get yearly and monthly summaries
        year_summary = summary_data[year]["summary"]
        month_summary = summary_data[year][month]

        # Initialize summary fields if missing
        for summary in [year_summary, month_summary]:
            summary.setdefault("total_income", 0.0)
            summary.setdefault("total_outcome", 0.0)
            summary.setdefault("net_balance", 0.0)
            summary.setdefault("total_transactions", {"income": 0, "outcome": 0})
            summary.setdefault("average", {"income": 0.0, "outcome": 0.0})
            summary.setdefault("highest", {
                "income": {"amount": 0.0, "category_id": None, "date": None},
                "outcome": {"amount": 0.0, "category_id": None, "date": None}
            })
            summary.setdefault("total_by_category", {"income": {}, "outcome": {}})

        # Update total values and transaction count
        if action == "add":
            year_summary[f"total_{transaction_type}"] += amount
            month_summary[f"total_{transaction_type}"] += amount
            year_summary["total_transactions"][transaction_type] += 1
            month_summary["total_transactions"][transaction_type] += 1

        elif action == "delete":
            year_summary[f"total_{transaction_type}"] -= amount
            month_summary[f"total_{transaction_type}"] -= amount
            year_summary["total_transactions"][transaction_type] -= 1
            month_summary["total_transactions"][transaction_type] -= 1

        elif action == "edit":
            old_amount = transaction["old_amount"]
            year_summary[f"total_{transaction_type}"] += (amount - old_amount)
            month_summary[f"total_{transaction_type}"] += (amount - old_amount)

        # Update net balance
        for summary in [year_summary, month_summary]:
            summary["net_balance"] = summary["total_income"] - summary["total_outcome"]

        # Update total by category
        for summary in [year_summary, month_summary]:
            category_totals = summary["total_by_category"][transaction_type]
            category_totals.setdefault(category_id, 0.0)

            if action == "add":
                category_totals[category_id] += amount
            elif action == "delete":
                category_totals[category_id] -= amount
                if category_totals[category_id] <= 0:
                    del category_totals[category_id]
            elif action == "edit":
                old_amount = transaction["old_amount"]
                category_totals[category_id] += (amount - old_amount)

        # Update highest income/outcome dynamically
        for summary in [year_summary, month_summary]:
            highest = summary["highest"][transaction_type]

            if action == "add" or (action == "edit" and amount > highest["amount"]):
                summary["highest"][transaction_type] = {"amount": amount, "category_id": category_id, "date": date_str}

            elif action == "delete" or (action == "edit" and amount < highest["amount"]):
                # Find the next highest transaction
                all_transactions = [
                    t for cat, t in summary["total_by_category"][transaction_type].items()
                ]
                new_highest = max(all_transactions, default=0.0)

                if new_highest > 0:
                    new_category_id = next(
                        (cat for cat, t in summary["total_by_category"][transaction_type].items() if t == new_highest),
                        None
                    )
                    summary["highest"][transaction_type] = {
                        "amount": new_highest,
                        "category_id": new_category_id,
                        "date": date_str  # Keeping last modified date
                    }
                else:
                    summary["highest"][transaction_type] = {"amount": 0.0, "category_id": None, "date": None}

        # Update average income/outcome
        for summary in [year_summary, month_summary]:
            total_trans = summary["total_transactions"][transaction_type]
            summary["average"][transaction_type] = (
                summary[f"total_{transaction_type}"] / total_trans if total_trans > 0 else 0.0
            )

        return summary_data

    async def check_balance(discord_id:str,income_type:str):
        ...
        
    async def add(discord_id:str,income_type:str,amount:int,detail:str,date:str):
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
        latest_id = max(map(int, json_file["income"]["by_id"].keys()), default=0)
        index = str(latest_id + 1)

        # Ensure date is in string format
        date_now = datetime.now().isoformat()

        # Insert new income entry
        transaction = {
            "category_id": income_type,
            "description": detail,
            "amount": amount,
            "date": date,
            "date_created": date_now,
            "is_deleted": False,
            "deleted_at": None
        }
        json_file["income"]["by_id"][index] = transaction

        # Ensure date hierarchy exists
        json_file["income"]["by_date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, [])
        json_file["income"]["by_date"][year][month][day].append(index)
        
        # Ensure by_category exists as a list
        json_file["income"]["by_category"].setdefault(income_type, [])
        json_file["income"]["by_category"][income_type].append(index)
        
        json_file = Income.update_summary(json_file,transaction,"add","income")
        # Write back to file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_file, file, indent=4)

        message = f"Success add Rp {amount} to balance"
        Income.logger.log(level=40,message=message)
        return True,message,None
    
    async def edit(discord_id:str,income_type:str,amount:int,detail:str,date:str):
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
        latest_id = max(map(int, json_file["income"]["by_id"].keys()), default=0)
        index = str(latest_id + 1)

        # Ensure date is in string format
        date_now = datetime.now().isoformat()

        # Insert new income entry
        transaction = {
            "category_id": income_type,
            "description": detail,
            "amount": amount,
            "date": date,
            "date_created": date_now,
            "is_deleted": False,
            "deleted_at": None
        }
        json_file["income"]["by_id"][index] = transaction

        # Ensure date hierarchy exists
        json_file["income"]["by_date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, [])
        json_file["income"]["by_date"][year][month][day].append(index)
        
        # Ensure by_category exists as a list
        json_file["income"]["by_category"].setdefault(income_type, [])
        json_file["income"]["by_category"][income_type].append(index)
        
        json_file = Income.update_summary(json_file,transaction,"add","income")
        # Write back to file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_file, file, indent=4)

        message = f"Success add Rp {amount} to balance"
        Income.logger.log(level=40,message=message)
        return True,message,None

    async def get_by_date(discord_id: str, date: str):
        year, month, day = date.split("-")
        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        
        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        
        transaction = json_file["income"]["by_date"].get(year,{}).get(month,{}).get(day,{})
        if not transaction:
            return False, "Transaction not found in database.", None
        
        user_language = User.get_user_language(discord_id)
        list_transaction = {}
        for id in transaction:
            category_id = json_file["income"]["by_id"][id]["category_id"]
            list_transaction[id] = json_file["income"]["by_id"][id]
            list_transaction[id]["category_name"] = json_file_category[discord_id]["income"][category_id]["description"][user_language]
            list_transaction[id]["emoticon"] = json_file_category[discord_id]["income"][category_id]["emoticon"]
            
        return True, "Data found", list_transaction
    
    async def delete(discord_id: str, id: str, date: str):
        year, month, day = date.split("-")

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)

        # Ensure transaction exists
        transaction = json_file["income"]["by_id"].get(id)
        if not transaction:
            return False, "Transaction not found in database.", None

        # Soft delete transaction
        transaction["is_deleted"] = True
        json_file["income"]["by_id"][id] = transaction

        # Safely remove ID from `by_date`
        try:
            json_file["income"]["by_date"][year][month][day].remove(id)
        except (KeyError, ValueError):
            pass  # Avoid error if ID is missing

        # Safely remove ID from `by_category`
        category_id = transaction.get("category_id")
        if category_id and category_id in json_file["income"]["by_category"]:
            try:
                json_file["income"]["by_category"][category_id].remove(id)
            except ValueError:
                pass

        # Update Summary
        json_file = Income.update_summary(json_file, transaction, "delete", "income")

        # Save Changes
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_file, file, indent=4)

        return True, "Transaction deleted successfully!", None
    
    async def get_daily_income(discord_id:str,date:str):
        day,month,year = date.split("-")

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        # If file is empty, initialize with template
        if not json_file:
            return False,"There's no income at that day",None
        
        income_data = json_file["income"]["by_date"].get(year,{}).get(month,{}).get(day,[])
        if len(income_data) == 0:
            return False,"There's no income this month",None
        
        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        message = f"**Income {date}**\n"
        title = f"Income Transaction of {date}"
        list_transaction_dict = {
            title:{}
        }
        for count,index in enumerate(income_data):
            transaction_data = json_file["income"]["by_id"][index]
            language = json_file_user[discord_id]["language"]
            income_type = json_file_category[discord_id]["income"][transaction_data["category_id"]]
            language = json_file_user[discord_id]["language"]
            income_type_name = income_type["description"][language]
            emoticon = income_type["emoticon"]
            amount = "{:,}".format(transaction_data["amount"]).replace(",", ".")
            submessage = f"{count+1}. Rp {amount} from {income_type_name} {emoticon}\n"
            message += submessage
            list_transaction_dict[title][index] = submessage
            
        return True,message,list_transaction_dict

    async def get_monthly_income(discord_id:str,date:str):
        
        month,year = date.split("-")

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False,"You have no transaction",None
        
        income_data = json_file["income"]["by_date"]
        list_transaction = Income.get_transactions_list(income_data,year,month) 
        if len(list_transaction) == 0:
            return False,"There's no income this month",None
        
        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        message = f"**Income {date}**\n"
        title = f"Montly income {date}"
        list_transaction_dict = {
            title:{}
        }
        for count,index in enumerate(list_transaction):
            transaction_data = json_file["income"]["by_id"][index]
            if transaction_data.get("is_deleted", True):
                continue
            
            income_type = json_file_category[discord_id]["income"][transaction_data["category_id"]]
            language = json_file_user[discord_id]["language"]
            income_type_name = income_type["description"][language]
            emoticon = income_type["emoticon"]
            amount = "{:,}".format(transaction_data["amount"]).replace(",", ".")
            message += f"{index}. Rp {amount} from {income_type} {emoticon}\n"
            
            list_transaction_dict[title][f"{count}. Income Transaction {transaction_data['date']}"] = f"**Rp {amount}** from **{income_type_name}** {emoticon}"
            
        
        return True,message,list_transaction_dict
    
    async def get_yearly_income(discord_id:str,year:str):
        
        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False,"You have no transaction",None
        
        income_data = json_file["income"]["by_date"]
        list_transaction = Income.get_transactions_list(income_data,year) 
        if len(list_transaction) == 0:
            return False,"There's no income this year",None
        
        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        message = f"**Income {year}**\n"
        title = f"Yearly income {year}"
        list_transaction_dict = {
            title:{}
        }
        for count,index in enumerate(list_transaction):
            transaction_data = json_file["income"]["by_id"][index]
            if transaction_data.get("is_deleted", True):
                continue
            
            income_type = json_file_category[discord_id]["income"][transaction_data["category_id"]]
            language = json_file_user[discord_id]["language"]
            income_type_name = income_type["description"][language]
            emoticon = income_type["emoticon"]
            amount = "{:,}".format(transaction_data["amount"]).replace(",", ".")
            message += f"{index}. Rp {amount} from {income_type} {emoticon}\n"
            
            list_transaction_dict[title][f"{count}. Income Transaction {transaction_data['date']}"] = f"**Rp {amount}** from **{income_type_name}** {emoticon}"
            
        
        return True,message,list_transaction_dict

    async def get_group_income():
        income = ""
        message = ""
        for index, data in enumerate(income):
            amount = "{:,}".format(data.amount).replace(",", ".")
            message += f"{index+1}. Rp {amount} from {data.name}\n"

        return message, income

    async def transfer(source:int,amount:int,target:int):
        
        list_type = temp_db._income_type
        data_date = date.today()
        #reducing
        await IncomeController.add(-abs(int(amount)), data_date, source,
                                   "Balancing transfer amount")

        await IncomeController.add(
            amount, data_date, target,
            f"Transfer balance from {list_type[int(source)-1].name}")

        amount = "{:,}".format(int(amount)).replace(",", ".")

        return f"Success transfer Rp {amount} from {list_type[int(source)-1].name} to {list_type[int(target)-1].name} "
