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

    async def check_balance(discord_id: str = "", income_type: str = ""):
        if not discord_id:
            return True, "Balance check skipped.", None

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False, "No transactions found.", None

        return True, "Balance check passed.", None
        
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

        message = f"Success add income: Rp {amount}"
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

        message = f"Success add income: Rp {amount}"
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
            return False,"There's no income for that day",None
        
        income_data = json_file["income"]["by_date"].get(year,{}).get(month,{}).get(day,[])
        if len(income_data) == 0:
            return False,"There's no income for that day",None
        
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
            message += f"{index}. Rp {amount} from {income_type_name} {emoticon}\n"
            
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
            message += f"{index}. Rp {amount} from {income_type_name} {emoticon}\n"
            
            list_transaction_dict[title][f"{count}. Income Transaction {transaction_data['date']}"] = f"**Rp {amount}** from **{income_type_name}** {emoticon}"
            
        
        return True,message,list_transaction_dict

    def _format_amount(amount: float) -> str:
        return "{:,}".format(int(amount)).replace(",", ".")

    def _get_income_balance_map(json_file: dict) -> dict:
        balances = {}
        for transaction in json_file.get("income", {}).get("by_id", {}).values():
            if transaction.get("is_deleted", True):
                continue
            category_id = str(transaction.get("category_id"))
            balances[category_id] = balances.get(category_id, 0) + transaction.get("amount", 0)

        for transaction in json_file.get("outcome", {}).get("by_id", {}).values():
            if transaction.get("is_deleted", True):
                continue
            income_category_id = transaction.get("income_category_id")
            if not income_category_id:
                continue
            income_category_id = str(income_category_id)
            balances[income_category_id] = balances.get(income_category_id, 0) - transaction.get("amount", 0)

        return balances

    def _get_income_category_balance(json_file: dict, category_id: str) -> float:
        balances = Income._get_income_balance_map(json_file)
        return balances.get(str(category_id), 0)

    async def get_income_balance_map(discord_id: str) -> dict:
        if not discord_id:
            return {}
        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return {}
        return Income._get_income_balance_map(json_file)

    async def get_monthly_summary(discord_id:str,date:str):
        month,year = date.split("-")

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False,"You have no transaction",None

        income_data = json_file.get("income", {}).get("by_date", {})
        outcome_data = json_file.get("outcome", {}).get("by_date", {})

        income_ids = Income.get_transactions_list(income_data,year,month)
        outcome_ids = Income.get_transactions_list(outcome_data,year,month)

        if len(income_ids) == 0 and len(outcome_ids) == 0:
            return False,"There's no transaction this month",None

        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        language = json_file_user.get(discord_id, {}).get("language", "en")

        income_totals = {}
        for index in income_ids:
            transaction_data = json_file["income"]["by_id"].get(index)
            if not transaction_data or transaction_data.get("is_deleted", True):
                continue
            category_id = str(transaction_data["category_id"])
            income_totals[category_id] = income_totals.get(category_id, 0) + transaction_data["amount"]

        outcome_totals = {}
        outcome_by_income = {}
        for index in outcome_ids:
            transaction_data = json_file["outcome"]["by_id"].get(index)
            if not transaction_data or transaction_data.get("is_deleted", True):
                continue
            category_id = str(transaction_data["category_id"])
            outcome_totals[category_id] = outcome_totals.get(category_id, 0) + transaction_data["amount"]

            income_category_id = transaction_data.get("income_category_id")
            if income_category_id:
                income_category_id = str(income_category_id)
                outcome_by_income[income_category_id] = outcome_by_income.get(income_category_id, 0) + transaction_data["amount"]

        income_title = f"Monthly income {date}"
        outcome_title = f"Monthly outcome {date}"
        remaining_title = f"Remaining by income type {date}"
        list_transaction_dict = {
            income_title: {},
            outcome_title: {},
            remaining_title: {},
        }

        if income_totals:
            for count, (category_id, total) in enumerate(
                sorted(income_totals.items(), key=lambda item: item[1], reverse=True), start=1
            ):
                category_data = json_file_category.get(discord_id, {}).get("income", {}).get(category_id, {})
                category_name = category_data.get("description", {}).get(language, category_id)
                emoticon = category_data.get("emoticon", "")
                amount = Income._format_amount(total)
                list_transaction_dict[income_title][str(count)] = f"Rp {amount} from {category_name} {emoticon}".strip()
        else:
            list_transaction_dict[income_title]["0"] = "No income this month."

        if outcome_totals:
            for count, (category_id, total) in enumerate(
                sorted(outcome_totals.items(), key=lambda item: item[1], reverse=True), start=1
            ):
                category_data = json_file_category.get(discord_id, {}).get("outcome", {}).get(category_id, {})
                category_name = category_data.get("description", {}).get(language, category_id)
                emoticon = category_data.get("emoticon", "")
                amount = Income._format_amount(total)
                list_transaction_dict[outcome_title][str(count)] = f"Rp {amount} for {category_name} {emoticon}".strip()
        else:
            list_transaction_dict[outcome_title]["0"] = "No outcome this month."

        remaining_count = 0
        for category_id, total in income_totals.items():
            remaining = total - outcome_by_income.get(category_id, 0)
            if remaining <= 0:
                continue
            remaining_count += 1
            category_data = json_file_category.get(discord_id, {}).get("income", {}).get(category_id, {})
            category_name = category_data.get("description", {}).get(language, category_id)
            emoticon = category_data.get("emoticon", "")
            amount = Income._format_amount(remaining)
            list_transaction_dict[remaining_title][str(remaining_count)] = f"Rp {amount} in {category_name} {emoticon}".strip()

        if remaining_count == 0:
            list_transaction_dict[remaining_title]["0"] = "No remaining balance for this month."

        return True,"Success",list_transaction_dict

    async def transfer_balance(discord_id:str,source_category:str,destination_category:str,amount:int,date:str,source_name:str="",destination_name:str=""):
        if source_category == destination_category:
            return False,"Source and destination categories must be different.",None

        amount = abs(int(amount))
        if amount <= 0:
            return False,"Amount must be greater than 0.",None

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            json_template = Util.read_json(JSON_TRANSACTION_TEMPLATE_FILE_PATH)
            with open(file_path, "w", encoding="utf-8") as file:
                json.dump(json_template, file, indent=4)
            json_file = Util.read_json(file_path)

        source_balance = Income._get_income_category_balance(json_file, source_category)
        if source_balance < amount:
            available_amount = Income._format_amount(source_balance)
            return False,f"Insufficient balance. Available: Rp {available_amount}",None

        date_now = datetime.now().isoformat()
        detail_source = f"Transfer to {destination_name or destination_category}"
        detail_destination = f"Transfer from {source_name or source_category}"

        next_id = max(map(int, json_file["income"]["by_id"].keys()), default=0) + 1

        def append_transaction(category_id: str, value: int, detail: str):
            nonlocal next_id, json_file
            year,month,day = date.split("-")
            index = str(next_id)
            next_id += 1
            transaction = {
                "category_id": category_id,
                "description": detail,
                "amount": value,
                "date": date,
                "date_created": date_now,
                "is_deleted": False,
                "deleted_at": None
            }
            json_file["income"]["by_id"][index] = transaction
            json_file["income"]["by_date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, [])
            json_file["income"]["by_date"][year][month][day].append(index)
            json_file["income"]["by_category"].setdefault(category_id, [])
            json_file["income"]["by_category"][category_id].append(index)
            json_file = Income.update_summary(json_file,transaction,"add","income")

        append_transaction(source_category, -amount, detail_source)
        append_transaction(destination_category, amount, detail_destination)

        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_file, file, indent=4)

        amount_format = Income._format_amount(amount)
        return True,f"Success transfer Rp {amount_format} from {source_name or source_category} to {destination_name or destination_category}",None

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
