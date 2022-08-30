from controller.Outcome import Outcome as OutcomeController
from controller.Transaction import Transaction as TransactionController
from datetime import datetime as date
class Outcome:
    async def add(msg:str):
        data = msg.split("-")
        transaction = await TransactionController.add()
        await OutcomeController.add(data[0],transaction.id,data[1],data[2])
        return f"Spend Rp {data[2]} for {data[1]}"
    
    async def get_daily_expense(msg):
        data_date = date.strptime(msg, "%Y-%m-%d")
        outcome = await OutcomeController.get_daily_expense(data_date)
        date_converted = date.strftime(outcome[0].date_created, "%d-%m-%Y")
        message = f"**DAILY EXPENSE ON** {date_converted}\n"
        for index, data in enumerate(outcome):
            message+= f"{index+1}. {data.detail_item} ({data.category.name}) Rp {data.amount}\n"

        return message

    async def get_monthly_expense(data_date):
        outcome = await OutcomeController.get_monthly_expense(data_date)
        date_converted = date.strftime(outcome[0].date_created, "%B")
        date_data = ""
        message = f"**MONTHLY EXPENSE ON {date_converted}**\n"
        for index, data in enumerate(outcome):
            if date_data != data.date_created:
                date_converted = date.strftime(data.date_created, "%d-%m-%Y")
                message += f"**{date_converted}**\n"
                date_data = data.date_created
            message+= f"{index+1}. {data.detail_item} ({data.category.name}) Rp {data.amount}\n"

        return message

    async def get_expense():
        outcome = await OutcomeController.get_expense()
        total = 0
        for i in outcome:
            total += i.amount
        return total
