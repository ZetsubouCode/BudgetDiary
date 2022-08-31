from controller.Income import Income as IncomeController
from controller.Transaction import Transaction as TransactionController
from datetime import date, timedelta
class Income:
    async def add(msg:str):
        data = msg.split("-")
        transaction = await TransactionController.add()
        if len(data)==3:
            detail = data[2]
        else:
            detail = None
        await IncomeController.add(transaction.id,data[0],data[1],detail)

        amount = "{:,}".format(data[0]).replace(",",".")
        return f"Success add Rp {amount} to balance"

    async def get_saving():
        income = await IncomeController.get_saving()
        total = 0
        for i in income:
            total += i.amount
        amount = "{:,}".format(total).replace(",",".")
        return total, amount

    async def get_last_saving():
        data_date = date.today().replace(day=1)
        income = await IncomeController.get_last_saving(data_date)
        total = 0
        for i in income:
            if i.amount is None:
                break
            total += i.amount
        return total

    async def get_this_month_saving(date_input, remaining):
        date_converted_a = date_input.replace(day=1)
        next_month = date_input.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        date_converted_b = next_month
        data = await IncomeController.get_this_month_saving(date_converted_a,date_converted_b)
        total = 0
        for i in data:
            total += i.amount
        month_name = date.strftime(next_month, "%B")
        total = "{:,}".format(total+remaining).replace(",",".")
        return f"Rp {total} for this month ({month_name})"
        
    async def get_detail_saving():
        income = await IncomeController.get_all()
        message = f"**Income**\n"
        for index,data in enumerate(income):
            amount = "{:,}".format(data.amount).replace(",",".")
            message += f"{index+1}. Rp {amount} from {data.type}\n"

        return message

