import json, os
from datetime import timedelta, date, datetime
from config.config import *
from util.date_utils import Util
from util.logger import LoggerSingleton
from .Income import Income


class Outcome:
    logger = LoggerSingleton.get_instance()

    def _normalize_category_map(category_data):
        if isinstance(category_data, dict):
            return category_data
        if isinstance(category_data, list):
            normalized = {}
            for item in category_data:
                category_id = item.get("id")
                if category_id is None:
                    continue
                normalized[str(category_id)] = {
                    "description": item.get("description", {}),
                    "emoticon": item.get("emoticon", ""),
                    "is_deleted": item.get("is_deleted", False),
                }
            return normalized
        return {}

    def _format_transaction_date(date_str: str) -> str:
        try:
            return datetime.strptime(date_str, "%Y-%m-%d").strftime("%d-%m-%Y")
        except Exception:
            return date_str

    async def add(discord_id:str,outcome_type:str,amount:int,detail:str,date:str,income_category_id: str = None):
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

        if income_category_id is not None:
            income_category_id = str(income_category_id)
            available_balance = Income._get_income_category_balance(json_file, income_category_id)
            if available_balance < amount:
                available_amount = Income._format_amount(max(available_balance, 0))
                return False, f"Insufficient balance. Available: Rp {available_amount}", None

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
        if income_category_id is not None:
            transaction["income_category_id"] = income_category_id
        json_file["outcome"]["by_id"][index] = transaction

        # Ensure date hierarchy exists
        json_file["outcome"]["by_date"].setdefault(year, {}).setdefault(month, {}).setdefault(day, [])
        json_file["outcome"]["by_date"][year][month][day].append(index)
        
        # Ensure by_category exists as a list
        json_file["outcome"]["by_category"].setdefault(outcome_type, [])
        json_file["outcome"]["by_category"][outcome_type].append(index)
        
        json_file = Income.update_summary(json_file,transaction,"add","outcome")
        # Write back to file
        with open(file_path, "w", encoding="utf-8") as file:
            json.dump(json_file, file, indent=4)

        message = f"Success add outcome: Rp {amount}"
        Outcome.logger.log(level=40,message=message)
        return True,message,None

    async def get_outcome_insight(discord_id: str, period: str, date_str: str, top_n: int = 3):
        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False, "You have no transaction", None

        outcome_data = json_file.get("outcome", {})
        by_date = outcome_data.get("by_date", {})
        by_id = outcome_data.get("by_id", {})

        if period == "daily":
            day, month, year = date_str.split("-")
            transaction_ids = by_date.get(year, {}).get(month, {}).get(day, [])
        elif period == "monthly":
            month, year = date_str.split("-")
            transaction_ids = Income.get_transactions_list(by_date, year, month)
        elif period == "yearly":
            year = date_str
            transaction_ids = Income.get_transactions_list(by_date, year)
        else:
            return False, "Invalid period.", None

        if not transaction_ids:
            return False, "No outcome found for this period.", None

        json_category = Util.read_json(JSON_CATEGORY_FILE_PATH).get(discord_id, {})
        categories = Outcome._normalize_category_map(json_category.get("outcome", {}))
        json_user = Util.read_json(JSON_USER_FILE_PATH).get(discord_id, {})
        language = json_user.get("language", "en")

        totals_by_category = {}
        total_amount = 0
        transaction_count = 0
        top_transaction = None

        for transaction_id in transaction_ids:
            transaction = by_id.get(transaction_id)
            if not transaction or transaction.get("is_deleted", False):
                continue

            try:
                amount = int(transaction.get("amount", 0))
            except (TypeError, ValueError):
                continue

            category_id = str(transaction.get("category_id"))
            totals_by_category[category_id] = totals_by_category.get(category_id, 0) + amount
            total_amount += amount
            transaction_count += 1

            if (top_transaction is None) or (amount > top_transaction["amount"]):
                top_transaction = {
                    "id": transaction_id,
                    "amount": amount,
                    "category_id": category_id,
                    "date": Outcome._format_transaction_date(transaction.get("date", "")),
                    "description": transaction.get("description", ""),
                }

        if transaction_count == 0:
            return False, "No outcome found for this period.", None

        def resolve_category(category_id: str):
            data = categories.get(category_id, {})
            description = data.get("description", {})
            name = (
                description.get(language)
                or description.get("en")
                or description.get("id")
                or f"Category {category_id}"
            )
            emoticon = data.get("emoticon", "")
            return name, emoticon

        category_rank = []
        for category_id, amount in sorted(totals_by_category.items(), key=lambda item: item[1], reverse=True):
            name, emoticon = resolve_category(category_id)
            category_rank.append({
                "category_id": category_id,
                "category_name": name,
                "emoticon": emoticon,
                "amount": amount,
                "percentage": (amount / total_amount) if total_amount else 0,
            })

        top_category = category_rank[0] if category_rank else None
        if top_transaction:
            name, emoticon = resolve_category(top_transaction["category_id"])
            top_transaction["category_name"] = name
            top_transaction["emoticon"] = emoticon

        data = {
            "period": period,
            "date_label": date_str,
            "total_amount": total_amount,
            "transaction_count": transaction_count,
            "top_category": top_category,
            "top_transaction": top_transaction,
            "top_categories": category_rank[:top_n],
        }
        return True, "Success", data

    async def get_daily_outcome(discord_id:str,date:str):
        day,month,year = date.split("-")

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        # If file is empty, initialize with template
        if not json_file:
            return False,"There's no outcome for that day",None

        outcome_data = json_file["outcome"]["by_date"].get(year,{}).get(month,{}).get(day,[])
        if len(outcome_data) == 0:
            return False,"There's no outcome for that day",None

        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        message = f"**Outcome {date}**\n"
        title = f"Outcome Transaction of {date}"
        list_transaction_dict = {
            title:{}
        }
        for count,index in enumerate(outcome_data):
            transaction_data = json_file["outcome"]["by_id"][index]
            language = json_file_user[discord_id]["language"]
            outcome_type = json_file_category[discord_id]["outcome"][transaction_data["category_id"]]
            outcome_type_name = outcome_type["description"][language]
            emoticon = outcome_type["emoticon"]
            amount = "{:,}".format(transaction_data["amount"]).replace(",", ".")
            submessage = f"{count+1}. Rp {amount} for {outcome_type_name} {emoticon}\n"
            message += submessage
            list_transaction_dict[title][index] = submessage

        return True,message,list_transaction_dict

    async def get_monthly_outcome(discord_id:str,date:str):
        month,year = date.split("-")

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False,"You have no transaction",None

        outcome_data = json_file["outcome"]["by_date"]
        list_transaction = Income.get_transactions_list(outcome_data,year,month)
        if len(list_transaction) == 0:
            return False,"There's no outcome this month",None

        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        message = f"**Outcome {date}**\n"
        title = f"Montly outcome {date}"
        list_transaction_dict = {
            title:{}
        }
        for count,index in enumerate(list_transaction):
            transaction_data = json_file["outcome"]["by_id"][index]
            if transaction_data.get("is_deleted", True):
                continue

            outcome_type = json_file_category[discord_id]["outcome"][transaction_data["category_id"]]
            language = json_file_user[discord_id]["language"]
            outcome_type_name = outcome_type["description"][language]
            emoticon = outcome_type["emoticon"]
            amount = "{:,}".format(transaction_data["amount"]).replace(",", ".")
            message += f"{index}. Rp {amount} for {outcome_type_name} {emoticon}\n"

            list_transaction_dict[title][f"{count}. Outcome Transaction {transaction_data['date']}"] = f"**Rp {amount}** for **{outcome_type_name}** {emoticon}"

        return True,message,list_transaction_dict

    async def get_yearly_outcome(discord_id:str,year:str):
        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False,"You have no transaction",None

        outcome_data = json_file["outcome"]["by_date"]
        list_transaction = Income.get_transactions_list(outcome_data,year)
        if len(list_transaction) == 0:
            return False,"There's no outcome this year",None

        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        message = f"**Outcome {year}**\n"
        title = f"Yearly outcome {year}"
        list_transaction_dict = {
            title:{}
        }
        for count,index in enumerate(list_transaction):
            transaction_data = json_file["outcome"]["by_id"][index]
            if transaction_data.get("is_deleted", True):
                continue

            outcome_type = json_file_category[discord_id]["outcome"][transaction_data["category_id"]]
            language = json_file_user[discord_id]["language"]
            outcome_type_name = outcome_type["description"][language]
            emoticon = outcome_type["emoticon"]
            amount = "{:,}".format(transaction_data["amount"]).replace(",", ".")
            message += f"{index}. Rp {amount} for {outcome_type_name} {emoticon}\n"

            list_transaction_dict[title][f"{count}. Outcome Transaction {transaction_data['date']}"] = f"**Rp {amount}** for **{outcome_type_name}** {emoticon}"

        return True,message,list_transaction_dict
