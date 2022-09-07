from controller.Income import Income as IncomeController
from datetime import date, datetime, timedelta
from temp_db import temp_db
class Income:
    async def add(msg:str):
        data = msg.split("#")
      
        if len(data)<2 or len(data)>4:
            return f"Input `{msg}` is not valid"
        try:
          int(data[0])
        except Exception as e:
          return f"Not a valid number ({str(e)})"
        if len(data)>=3:
            detail = data[2]
        else:
            detail = None

        if len(data)==4:
            try:
                data_date = datetime.strptime(data[3],"%d-%m-%Y")
                data_date = datetime.strftime(data_date, "%Y-%m-%d")
            except ValueError as e:
                return f"Incorrect data format, should be YYYY-MM-DD -> {str(e)}" 
        else:
            data_date = date.today()

        await IncomeController.add(data[0],data_date,data[1],detail)

        amount = "{:,}".format(int(data[0])).replace(",",".")
        return f"Success add Rp {amount} to balance"

    async def get_saving():
        income = await IncomeController.get_daily_income()
        total = 0
        for i in income:
            if i.amount is None:
              break
            total += i.amount
        amount = "{:,}".format(total).replace(",",".")
        return total, amount

    async def get_last_income():
        data_date = date.today().replace(day=1)
        income = await IncomeController.get_last_income(data_date)
        total = 0
        for i in income:
            if i.amount is None:
                break
            total += i.amount
        return total

    async def get_this_month_income(date_input, remaining):
        date_converted_a = date_input.replace(day=1)
        next_month = date_input.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        date_converted_b = next_month
        data = await IncomeController.get_this_month_income(date_converted_a,date_converted_b)
        total = 0
        for i in data:
            if i.amount == None:
              break
            total += i.amount
        month_name = date.strftime(next_month, "%B")
        total = "{:,}".format(total+remaining).replace(",",".")
        return f"Rp {total} for this month ({month_name})"
        
    async def get_monthly_income(input_date):
        next_month = input_date.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        income = await IncomeController.get_monthly_income(input_date.replace(day=1),next_month)
        if len(income) <= 0:
          return "There's no income this month"
        message = f"**Income {input_date}**\n"
        for index,data in enumerate(income):
            amount = "{:,}".format(data.amount).replace(",",".")
            message += f"{index+1}. Rp {amount} from {data.income_type.name}\n"

        return message

    async def transfer(msg:str):
        data = msg.split("#")
      
        if len(data)!=3:
            return f"Input `{msg}` is not valid"
        try:
          int(data[1])
        except Exception as e:
          return f"Not a valid number ({str(e)})"
        
        data_date = date.today()
        next_month = data_date.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        
        list_type = temp_db._income_type
        income = await IncomeController.get_by_income_type_and_date(data[0],data_date.replace(day=1),next_month)
        
        if not income:
            return f"There is no income available in {list_type[int(data[0]-1)].name}"
        income_amount = 0
        for income_data in income:
            if income_data.amount >income_amount:
                income_amount = income_data.amount
                data_income = income_data
        await IncomeController.reduce_amount_by_id(data_income.id,data[1])

        await IncomeController.add(data[1],data_date,data[2],"Transfer balance")

        amount = "{:,}".format(int(data[1])).replace(",",".")

        return f"Success transfer Rp {amount} from {list_type[int(data[0])-1].name} to {list_type[int(data[2])-1].name} "


