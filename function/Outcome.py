from controller.Outcome import Outcome as OutcomeController
from datetime import timedelta, date, datetime
from utils import Util

class Outcome:

    async def add(outcome_type:int,income_type:int,amount:int,detail:str,date:str):
        input_date = Util.date_validation(date)
        if outcome_type == '7':
            amount = -abs(int(amount))
            await OutcomeController.add(amount, input_date, income_type,
                                        "Balancing balance amount")
        await OutcomeController.add(outcome_type, income_type, detail, amount, input_date)

        amount = "{:,}".format(abs(int(amount))).replace(",", ".")
        return f"Spend Rp {amount} for {detail}"

    async def get_daily_outcome(date:str):
        input_date = Util.date_validation(date)
        outcome = await OutcomeController.get_daily_outcome(input_date)
        if outcome:
            date_converted = datetime.strftime(outcome[0].date_created,
                                               "%d-%m-%Y")
            message = f"**DAILY OUTCOME ON** {date_converted}\n"
        else:
            message = "There's no outcome on this day"
        for index, data in enumerate(outcome):
            amount = "{:,}".format(data.amount).replace(",", ".")
            message += f"{index+1}. [**{data.income_type.name}**] {data.category.emoticon} {data.detail_item} Rp {amount}\n"

        return message

    async def get_monthly_outcome_json(input_date):
        temp={}
        date_converted_a ,date_converted_b = Util.get_first_and_last_day(input_date)
        outcome = await OutcomeController.get_monthly_outcome(
            date_converted_a ,date_converted_b)
        if outcome:
            date_converted = datetime.strftime(outcome[0].date_created, "%B")
            title= f"**MONTHLY OUTCOME ON {date_converted}**\n"
        else:
            return "There's no outcome on this month"
        date_data = ""
        for index, data in enumerate(outcome):
            if date_data != data.date_created:
                date_converted = datetime.strftime(data.date_created,"%d-%m-%Y")
                data_message = date_converted
                date_data = data.date_created
                
            amount = "{:,}".format(data.amount).replace(",", ".")
            key = f"Transaction {index+1}"
            data = f"{data.category.emoticon}  [**{data.income_type.name}**] {data.detail_item} Rp {amount}\n"
            if str(data_message) not in temp:
                temp.update({str(data_message):{key:data}})
            else :
                temp[str(data_message)][key] = data

        return title,temp

    async def get_group_outcome():
        outcome = await OutcomeController.get_group_outcome()
        message = ""
        for index, data in enumerate(outcome):
            amount = "{:,}".format(data.amount).replace(",", ".")
            message += f"{index+1}. Rp {amount} from {data.name}\n"

        return message, outcome

    async def get_outcome():
        outcome = await OutcomeController.get_outcome()
        total = 0
        for i in outcome:
            if i.amount is None:
                break
            total += i.amount
        amount = "{:,}".format(total).replace(",", ".")
        return total, amount

    async def get_last_outcome():
        input_date = date.today().replace(day=1)
        outcome = await OutcomeController.get_last_outcome(input_date)
        total = 0
        for i in outcome:
            if i.amount is None:
                break
            total += i.amount

        return total

    async def get_monthly_total(date_input: date):
        next_month = date_input.replace(day=28) + timedelta(days=4)
        next_month = next_month - timedelta(days=next_month.day)
        outcome = await OutcomeController.get_monthly_total(
            date_input, next_month)
        return outcome[0].amount