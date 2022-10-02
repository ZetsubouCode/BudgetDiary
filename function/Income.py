from controller.Income import Income as IncomeController
from datetime import date, datetime, timedelta
from temp_db import temp_db
from utils import Util

class Income:
    
    async def add(income_type,amount,detail,date):
        
        data_date = Util.date_validation(date)

        await IncomeController.add(amount, data_date, income_type, detail)

        amount = "{:,}".format(int(amount)).replace(",", ".")
        return f"Success add Rp {amount} to balance"

    async def get_daily_income(date):

        data_date = Util.date_validation(date)

        income = await IncomeController.get_daily_income(data_date)
        if len(income) <= 0:
            return "There's no income this month"
        message = f"**Income {data_date}**\n"
        for index, data in enumerate(income):
            amount = "{:,}".format(data.amount).replace(",", ".")
            message += f"{index+1}. Rp {amount} from {data.income_type.name}\n"
        return message

    async def get_last_income():
        data_date = date.today().replace(day=1)
        income = await IncomeController.get_last_income(data_date)
        total = 0
        for i in income:
            if i.amount is None:
                break
            total += i.amount
        return total

    async def get_this_month_income(input_date, remaining):
        date_converted_a ,date_converted_b = Util.get_first_and_last_day(input_date)
        data = await IncomeController.get_this_month_income(
            date_converted_a, date_converted_b)
        total = 0
        for i in data:
            if i.amount == None:
                break
            total += i.amount
        month_name = date.strftime(date_converted_b, "%B")
        total = "{:,}".format(total + remaining).replace(",", ".")
        return f"Rp {total} for this month ({month_name})"

    async def get_monthly_income(input_date):
        date_converted_a ,date_converted_b = Util.get_first_and_last_day(input_date)
        income = await IncomeController.get_monthly_income(
            date_converted_a, date_converted_b)
        if len(income) <= 0:
            return "There's no income this month"
        message = f"**Income {input_date}**\n"
        for index, data in enumerate(income):
            amount = "{:,}".format(data.amount).replace(",", ".")
            message += f"{index+1}. Rp {amount} from {data.income_type.name}\n"

        return message

    async def get_group_income():
        income = await IncomeController.get_group_income()
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
