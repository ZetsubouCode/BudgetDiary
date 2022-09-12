from controller.Outcome import Outcome as OutcomeController
from datetime import timedelta, date, datetime

class Outcome:

    async def add(msg: str):
        data = msg.split("#")
        if len(data) > 5 or len(data) < 4:
            return f"Input `{msg}` is not valid"
        try:
            test = int(data[3])
        except ValueError as e:
            return f"Not a valid number ({str(e)})"
        if len(data) == 5:
            try:
                data_date = datetime.strptime(data[4], "%d-%m-%Y")
                data_date = datetime.strftime(data_date, "%Y-%m-%d")
            except ValueError as e:
                return f"Incorrect data format, should be YYYY-MM-DD -> {str(e)}"
        else:
            data_date = date.today()
        if data[0] == '7':
            amount = -abs(int(data[3]))
            await OutcomeController.add(amount, data_date, data[1],
                                        "Balancing balance amount")
        await OutcomeController.add(data[0], data[1], data[2], data[3],
                                    data_date)

        amount = "{:,}".format(int(data[3])).replace(",", ".")
        return f"Spend Rp {amount} for {data[2]}"

    async def get_daily_outcome(msg):
        try:
            data_date = datetime.strptime(msg, "%Y-%m-%d")
        except Exception as e:
            return f"Date format is invalid -> {str(e)}"
        outcome = await OutcomeController.get_daily_outcome(data_date)
        if outcome:
            date_converted = datetime.strftime(outcome[0].date_created,
                                               "%d-%m-%Y")
            message = f"**DAILY OUTCOME ON** {date_converted}\n"
        else:
            message = "There's no outcome on this day"
        for index, data in enumerate(outcome):
            amount = "{:,}".format(data.amount).replace(",", ".")
            message += f"{index+1}. [{data.category.name}] {data.detail_item} Rp {amount}\n"

        return message

    async def get_monthly_outcome(data_date):
        next_month = data_date.replace(day=28) + timedelta(days=4)
        next_month = next_month - timedelta(days=next_month.day)
        outcome = await OutcomeController.get_monthly_outcome(
            data_date.replace(day=1), next_month)
        if outcome:
            date_converted = datetime.strftime(outcome[0].date_created, "%B")
            message = f"**MONTHLY OUTCOME ON {date_converted}**\n"
        else:
            return "There's no outcome on this month"
        date_data = ""
        list_message = []
        for index, data in enumerate(outcome):
            if date_data != data.date_created:
                date_converted = datetime.strftime(data.date_created,
                                                   "%d-%m-%Y")
                data_message = f"**{date_converted}**\n"
                if len(message+data_message) > 2000:
                  list_message.append(message)
                  message = ""
                message += data_message
                date_data = data.date_created

            amount = "{:,}".format(data.amount).replace(",", ".")
            data_message = f"{index+1}. [**{data.category.name}**] {data.detail_item} Rp {amount}\n"
            if len(message+data_message) > 2000:
              list_message.append(message)
              message = ""
            message += data_message

        list_message.append(message)
          
        return list_message

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
        data_date = date.today().replace(day=1)
        outcome = await OutcomeController.get_last_outcome(data_date)
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