from controller.Outcome import Outcome as OutcomeController
from controller.Transaction import Transaction as TransactionController
from datetime import timedelta,date,datetime
class Outcome:
    async def add(msg:str):
        data = msg.split("-")
        transaction = await TransactionController.add()
        await OutcomeController.add(data[0],transaction.id,data[1],data[2])
        amount = "{:,}".format(int(data[2])).replace(",",".")
        return f"Spend Rp {amount} for {data[1]}"
    
    async def get_daily_expense(msg):
        data_date = datetime.strptime(msg, "%Y-%m-%d")
        outcome = await OutcomeController.get_daily_expense(data_date)
        if outcome:
            date_converted = datetime.strftime(outcome[0].date_created, "%d-%m-%Y")
            message = f"**DAILY EXPENSE ON** {date_converted}\n"
        else:
            message = "There's no expense on this day"
        for index, data in enumerate(outcome):
            amount = "{:,}".format(data.amount).replace(",",".")
            message+= f"{index+1}. [{data.category.name}] {data.detail_item} Rp {amount}\n"

        return message

    async def get_monthly_expense(data_date):
        next_month = data_date.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        outcome = await OutcomeController.get_monthly_expense(data_date.replace(day=1),next_month)
        if outcome:
            date_converted = datetime.strftime(outcome[0].date_created, "%B")
            message = f"**MONTHLY EXPENSE ON {date_converted}**\n"
        else:
            message = "There's no expense on this month"
        date_data = ""
        for index, data in enumerate(outcome):
            if date_data != data.date_created:
                date_converted = datetime.strftime(data.date_created, "%d-%m-%Y")
                message += f"**{date_converted}**\n"
                date_data = data.date_created
                amount = "{:,}".format(data.amount).replace(",",".")
            message+= f"{index+1}. {data.detail_item} ({data.category.name}) Rp {amount}\n"

        return message

    async def get_expense():
        outcome = await OutcomeController.get_expense()
        total = 0
        for i in outcome:
            total += i.amount
        amount = "{:,}".format(total).replace(",",".")
        return total, amount

    async def get_last_expense():
        data_date = date.today().replace(day=1)
        outcome = await OutcomeController.get_last_expense(data_date)
        total = 0
        for i in outcome:
            if i.amount is None:
                break
            total += i.amount

        return total
