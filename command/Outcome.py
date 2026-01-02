import json, os
from datetime import timedelta, date, datetime
from config.config import *
from util.date_utils import Util
from util.logger import LoggerSingleton
from .Income import Income


class Outcome:
    logger = LoggerSingleton.get_instance()

    def _get_month_names(language: str) -> list:
        if language == "id":
            return [
                "Januari",
                "Februari",
                "Maret",
                "April",
                "Mei",
                "Juni",
                "Juli",
                "Agustus",
                "September",
                "Oktober",
                "November",
                "Desember",
            ]
        return [
            "January",
            "February",
            "March",
            "April",
            "May",
            "June",
            "July",
            "August",
            "September",
            "October",
            "November",
            "December",
        ]

    def _get_default_detail(language: str) -> str:
        default_detail = {
            "id": "Tanpa keterangan",
            "en": "No detail",
        }
        return default_detail.get(language, default_detail["en"])

    def _format_amount(amount: int) -> str:
        try:
            amount_value = int(round(amount))
        except (TypeError, ValueError):
            amount_value = 0
        return "{:,}".format(amount_value).replace(",", ".")

    def _format_month_year_label(month: str, year: str, language: str) -> str:
        try:
            month_index = int(month) - 1
            month_name = Outcome._get_month_names(language)[month_index]
            return f"{month_name} {year}"
        except (ValueError, IndexError):
            return f"{month}-{year}"

    def _format_date_label(date_str: str, language: str) -> str:
        for fmt in ("%d-%m-%Y", "%Y-%m-%d"):
            try:
                date_obj = datetime.strptime(date_str, fmt)
                month_name = Outcome._get_month_names(language)[date_obj.month - 1]
                return f"{date_obj.day} {month_name} {date_obj.year}"
            except ValueError:
                continue
        return date_str

    def _format_outcome_line(index: int, amount: int, category_name: str, emoticon: str, detail: str, language: str, date_label: str = None) -> str:
        amount_text = Outcome._format_amount(amount)
        category_label = f"{category_name} {emoticon}".strip()
        detail_text = (detail or "").strip() or Outcome._get_default_detail(language)
        if language == "id":
            sentence = f"{index}. Rp {amount_text} untuk {category_label}. Keterangan: {detail_text}."
            if date_label:
                sentence = f"{sentence} Tanggal: {date_label}."
            return sentence
        sentence = f"{index}. Rp {amount_text} for {category_label}. Detail: {detail_text}."
        if date_label:
            sentence = f"{sentence} Date: {date_label}."
        return sentence

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

    def _resolve_category_name(category_data: dict, language: str, fallback: str) -> str:
        description = category_data.get("description", {})
        return (
            description.get(language)
            or description.get("en")
            or description.get("id")
            or fallback
        )

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
        language = json_file_user.get(discord_id, {}).get("language", "en")
        date_label = Outcome._format_date_label(date, language)
        message = f"**Outcome {date_label}**\n"
        title = f"Outcome {date_label}"
        list_transaction_dict = {
            title:{}
        }
        display_index = 0
        for index in outcome_data:
            transaction_data = json_file["outcome"]["by_id"][index]
            if transaction_data.get("is_deleted", True):
                continue
            outcome_type = json_file_category[discord_id]["outcome"][transaction_data["category_id"]]
            emoticon = outcome_type["emoticon"]
            outcome_type_name = Outcome._resolve_category_name(outcome_type, language, f"Category {transaction_data['category_id']}")
            detail = transaction_data.get("description", "")
            display_index += 1
            message_line = Outcome._format_outcome_line(
                display_index,
                transaction_data.get("amount", 0),
                outcome_type_name,
                emoticon,
                detail,
                language,
            )
            message += f"{message_line}\n"
            list_transaction_dict[title][str(display_index)] = message_line

        if display_index == 0:
            return False,"There's no outcome for that day",None

        return True,message,list_transaction_dict

    async def get_monthly_outcome(discord_id:str,date:str):
        month,year = date.split("-")

        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False,"You have no transaction",None

        outcome_data = json_file["outcome"]["by_date"]
        month_data = outcome_data.get(year, {}).get(month, {})
        if not month_data:
            return False,"There's no outcome this month",None

        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        language = json_file_user.get(discord_id, {}).get("language", "en")
        month_label = Outcome._format_month_year_label(month, year, language)
        message = f"**Outcome {month_label}**\n"
        list_transaction_dict = {}
        has_data = False
        for day in sorted(month_data.keys(), key=lambda item: int(item)):
            day_transactions = month_data.get(day, [])
            display_index = 0
            day_lines = {}
            for index in day_transactions:
                transaction_data = json_file["outcome"]["by_id"][index]
                if transaction_data.get("is_deleted", True):
                    continue

                display_index += 1
                outcome_type = json_file_category[discord_id]["outcome"][transaction_data["category_id"]]
                emoticon = outcome_type["emoticon"]
                outcome_type_name = Outcome._resolve_category_name(outcome_type, language, f"Category {transaction_data['category_id']}")
                detail = transaction_data.get("description", "")
                message_line = Outcome._format_outcome_line(
                    display_index,
                    transaction_data.get("amount", 0),
                    outcome_type_name,
                    emoticon,
                    detail,
                    language,
                )
                message += f"{message_line}\n"
                day_lines[str(display_index)] = message_line

            if day_lines:
                has_data = True
                date_label = Outcome._format_date_label(f"{day}-{month}-{year}", language)
                list_transaction_dict[date_label] = day_lines
        if not has_data:
            return False,"There's no outcome this month",None

        return True,message,list_transaction_dict

    async def get_yearly_outcome(discord_id:str,year:str):
        file_path = os.path.join(JSON_TRANSACTION_FILE_PATH, f"{discord_id}.json")
        json_file = Util.read_json(file_path)
        if not json_file:
            return False,"You have no transaction",None

        outcome_data = json_file["outcome"]["by_date"]
        year_data = outcome_data.get(year, {})
        if not year_data:
            return False,"There's no outcome this year",None

        json_file_category = Util.read_json(JSON_CATEGORY_FILE_PATH)
        json_file_user = Util.read_json(JSON_USER_FILE_PATH)
        language = json_file_user.get(discord_id, {}).get("language", "en")
        message = f"**Outcome {year}**\n"
        list_transaction_dict = {}
        by_id = json_file.get("outcome", {}).get("by_id", {})
        has_data = False
        for month in sorted(year_data.keys(), key=lambda item: int(item)):
            month_days = year_data.get(month, {})
            totals_by_category = {}
            counts_by_category = {}
            daily_totals = {}
            total_amount = 0
            total_transactions = 0
            active_days = set()
            top_transaction = None

            for day in sorted(month_days.keys(), key=lambda item: int(item)):
                day_transactions = month_days.get(day, [])
                day_has_transaction = False
                day_total = 0
                for index in day_transactions:
                    transaction_data = by_id.get(index)
                    if not transaction_data or transaction_data.get("is_deleted", True):
                        continue

                    try:
                        amount = int(transaction_data.get("amount", 0))
                    except (TypeError, ValueError):
                        continue

                    day_has_transaction = True
                    day_total += amount
                    total_amount += amount
                    total_transactions += 1

                    category_id = str(transaction_data.get("category_id"))
                    totals_by_category[category_id] = totals_by_category.get(category_id, 0) + amount
                    counts_by_category[category_id] = counts_by_category.get(category_id, 0) + 1

                    if (top_transaction is None) or (amount > top_transaction["amount"]):
                        top_transaction = {
                            "amount": amount,
                            "category_id": category_id,
                            "date": transaction_data.get("date", ""),
                            "description": transaction_data.get("description", ""),
                        }

                if day_has_transaction:
                    active_days.add(day)
                    daily_totals[day] = day_total

            if total_transactions == 0:
                continue

            def resolve_category_label(category_id: str) -> str:
                category_data = json_file_category.get(discord_id, {}).get("outcome", {}).get(category_id, {})
                category_name = Outcome._resolve_category_name(category_data, language, f"Category {category_id}")
                emoticon = category_data.get("emoticon", "")
                return f"{category_name} {emoticon}".strip()

            top_count_category = max(
                counts_by_category.keys(),
                key=lambda cid: (counts_by_category.get(cid, 0), totals_by_category.get(cid, 0)),
            )
            top_amount_category = max(
                totals_by_category.keys(),
                key=lambda cid: totals_by_category.get(cid, 0),
            )
            top_day = max(daily_totals.keys(), key=lambda d: daily_totals.get(d, 0)) if daily_totals else None

            month_label = Outcome._format_month_year_label(month, year, language)
            month_lines = []
            amount_text = Outcome._format_amount(total_amount)
            avg_amount = Outcome._format_amount(total_amount / total_transactions) if total_transactions else Outcome._format_amount(0)
            active_days_count = len(active_days)
            category_count = len(counts_by_category)

            if language == "id":
                month_lines.append(f"Ringkasan {month_label}")
                month_lines.append(f"Total pengeluaran: Rp {amount_text}")
                month_lines.append(f"Total transaksi: {total_transactions}")
                month_lines.append(f"Hari aktif: {active_days_count}")
                month_lines.append(f"Kategori aktif: {category_count}")
                month_lines.append(f"Rata-rata per transaksi: Rp {avg_amount}")
                month_lines.append("")
                month_lines.append("Sorotan")
                month_lines.append(
                    f"Kategori transaksi terbanyak: {resolve_category_label(top_count_category)} ({counts_by_category.get(top_count_category, 0)} transaksi, Rp {Outcome._format_amount(totals_by_category.get(top_count_category, 0))})"
                )
                month_lines.append(
                    f"Kategori terboros: {resolve_category_label(top_amount_category)} (Rp {Outcome._format_amount(totals_by_category.get(top_amount_category, 0))})"
                )
                if top_transaction:
                    top_detail = (top_transaction.get("description") or "").strip() or Outcome._get_default_detail(language)
                    top_date = Outcome._format_date_label(top_transaction.get("date", ""), language)
                    month_lines.append(
                        f"Transaksi termahal: Rp {Outcome._format_amount(top_transaction.get('amount', 0))} untuk {resolve_category_label(top_transaction.get('category_id'))} pada {top_date}"
                    )
                    month_lines.append(f"Keterangan: {top_detail}")
                if top_day:
                    top_day_label = Outcome._format_date_label(f"{top_day}-{month}-{year}", language)
                    month_lines.append(
                        f"Hari terboros: {top_day_label} (Rp {Outcome._format_amount(daily_totals.get(top_day, 0))})"
                    )
                month_lines.append("")
                month_lines.append("Rincian kategori")
            else:
                month_lines.append(f"Summary {month_label}")
                month_lines.append(f"Total spending: Rp {amount_text}")
                month_lines.append(f"Total transactions: {total_transactions}")
                month_lines.append(f"Active days: {active_days_count}")
                month_lines.append(f"Active categories: {category_count}")
                month_lines.append(f"Average per transaction: Rp {avg_amount}")
                month_lines.append("")
                month_lines.append("Highlights")
                month_lines.append(
                    f"Most frequent category: {resolve_category_label(top_count_category)} ({counts_by_category.get(top_count_category, 0)} transactions, Rp {Outcome._format_amount(totals_by_category.get(top_count_category, 0))})"
                )
                month_lines.append(
                    f"Top spending category: {resolve_category_label(top_amount_category)} (Rp {Outcome._format_amount(totals_by_category.get(top_amount_category, 0))})"
                )
                if top_transaction:
                    top_detail = (top_transaction.get("description") or "").strip() or Outcome._get_default_detail(language)
                    top_date = Outcome._format_date_label(top_transaction.get("date", ""), language)
                    month_lines.append(
                        f"Most expensive transaction: Rp {Outcome._format_amount(top_transaction.get('amount', 0))} for {resolve_category_label(top_transaction.get('category_id'))} on {top_date}"
                    )
                    month_lines.append(f"Detail: {top_detail}")
                if top_day:
                    top_day_label = Outcome._format_date_label(f"{top_day}-{month}-{year}", language)
                    month_lines.append(
                        f"Highest spending day: {top_day_label} (Rp {Outcome._format_amount(daily_totals.get(top_day, 0))})"
                    )
                month_lines.append("")
                month_lines.append("Category breakdown")

            for idx, (category_id, amount) in enumerate(sorted(totals_by_category.items(), key=lambda item: item[1], reverse=True), start=1):
                category_label = resolve_category_label(category_id)
                count = counts_by_category.get(category_id, 0)
                amount_label = Outcome._format_amount(amount)
                if language == "id":
                    month_lines.append(f"{idx}. {category_label} - {count} transaksi, Rp {amount_label}")
                else:
                    month_lines.append(f"{idx}. {category_label} - {count} transactions, Rp {amount_label}")

            has_data = True
            summary_text = "\n".join(month_lines)
            list_transaction_dict[month_label] = {"1": summary_text}
            message += f"\n{month_label}\n" + "\n".join(month_lines) + "\n"
        if not has_data:
            return False,"There's no outcome this year",None

        return True,message,list_transaction_dict
