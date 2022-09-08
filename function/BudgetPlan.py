from controller.BudgetPlan import BudgetPlan as BudgetPlanController
from datetime import timedelta,date,datetime
class BudgetPlan:
    async def add(msg:str):
        data = msg.split("#")
        if len(data)>4 or len(data)<3:
            return f"Input `{msg}` is not valid"
        try:
          test = int(data[2])
        except ValueError as e:
          return f"Not a valid number ({str(e)})"

        if len(data)==4:
            detail = data[3]
        else:
            detail = None
        try:
            data_date = datetime.strptime(data[1],"%d-%m-%Y")
            data_date = datetime.strftime(data_date, "%Y-%m-%d")
        except ValueError as e:
            return f"Incorrect data format, should be YYYY-MM-DD -> {str(e)}" 

        await BudgetPlanController.add(data[0],data_date,detail,data[2])
      
        amount = "{:,}".format(int(data[2])).replace(",",".")
        return f"Planning to spend Rp {amount} for {detail} on {data_date}"

    async def get_monthly_budget_plan(data_date):
        next_month = data_date.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        budget_plan = await BudgetPlanController.get_monthly_budget_plan(data_date.replace(day=1),next_month)
        if budget_plan:
            date_converted = datetime.strftime(budget_plan[0].date_buy, "%B")
            message = f"**MONTHLY BUDGET PLAN ON {date_converted}**\n"
        else:
            return "There's no budget_plan on this month"
        date_data = ""
        for index, data in enumerate(budget_plan):
            if date_data != data.date_buy:
                date_converted = datetime.strftime(data.date_buy, "%d-%m-%Y")
                message += f"**{date_converted}**\n"
                date_data = data.date_buy
            if data.detail:
                detail = data.detail+" "
            else:
                detail = ""
              
            amount = "{:,}".format(data.amount).replace(",",".")
            message+= f"{index+1}. [**{data.category.name}**] {detail}Rp {amount} on {data.date_buy}\n"

        return message

    async def get_monthly_total(date_input:date):
        next_month = date_input.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        budget_plan = await BudgetPlanController.get_monthly_total(date_input,next_month)
        return budget_plan[0].amount
