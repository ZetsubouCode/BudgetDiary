from controller.Income import Income as IncomeController
from controller.Transaction import Transaction as TransactionController
from datetime import date, timedelta
class Income:
    async def add(msg:str):
        data = msg.split("-")
        transaction = await TransactionController.add()
        print(data)
        if len(data)==3:
            detail = data[2]
        else:
            detail = None
        await IncomeController.add(transaction.id,data[0],data[1],detail)
        return f"Success add {data[0]} to balance"

    async def get_saving():
        data = await IncomeController.get_saving()
        total = 0
        for i in data:
            total += i.amount
        return total

    async def get_this_month_saving(date_input):
        date_converted_a = date_input.replace(day=1)
        next_month = date_input.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        date_converted_b = next_month
        data = await IncomeController.get_this_month_saving(date_converted_a,date_converted_b)
        total = 0
        for i in data:
            total += i.amount
        month_name = date.strftime(next_month, "%B")
        return f"Rp {total} for this month ({month_name})"
        
    async def get_detail_saving():
        income = await IncomeController.get_all()
        message = f"**Income**\n"
        for index,data in enumerate(income):
            message += f"{index+1}. Rp {data.amount} from {data.type}\n"

        return message

