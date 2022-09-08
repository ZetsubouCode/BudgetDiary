from controller.SavingPlan import SavingPlan as SavingPlanController
from datetime import timedelta,date,datetime
class SavingPlan:
    async def add(msg:str):
        data = msg.split("#")
      
        if len(data)!=3:
            return f"Input `{msg}` is not valid"
        try:
          int(data[2])
        except Exception as e:
          return f"Not a valid number ({str(e)})"

        try:
            data_date = datetime.strptime(data[1],"%d-%m-%Y")
            data_date = datetime.strftime(data_date, "%Y-%m-%d")
        except ValueError as e:
            return f"Incorrect data format, should be YYYY-MM-DD -> {str(e)}" 

        await SavingPlanController.add(data[0],data_date,data[1])

        amount = "{:,}".format(int(data[0])).replace(",",".")
        return f"Success add Rp {amount} to balance"

    async def get_monthly_saving_plan(data_date):
        next_month = data_date.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        saving_plan = await SavingPlanController.get_monthly_saving_plan(data_date.replace(day=1),next_month)
        if saving_plan:
            date_converted = datetime.strftime(saving_plan[0].date_created, "%B")
            message = f"**MONTHLY OUTCOME ON {date_converted}**\n"
        else:
            return "There's no saving_plan on this month"
        date_data = ""
        for index, data in enumerate(saving_plan):
            if date_data != data.date_created:
                date_converted = datetime.strftime(data.date_created, "%d-%m-%Y")
                message += f"**{date_converted}**\n"
                date_data = data.date_created
              
            amount = "{:,}".format(data.amount).replace(",",".")
            message+= f"{index+1}. [**{data.category.name}**] {data.detail_item} Rp {amount}\n"

        return message

    async def get_saving_plan_total():
        saving_plan = await SavingPlanController.get_monthly_total()
        total = 0
        for i in saving_plan:
            if i.amount is None:
              break
            total += i.amount
        amount = "{:,}".format(total).replace(",",".")
        return total, amount