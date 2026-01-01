from controller.LimitPlan import LimitPlan as LimitPlanController
from datetime import timedelta,date,datetime
class LimitPlan:
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
            if int(data[1]) > 12 or int(data[1]) < 1:
                return f"Please input correctly. {data.content} is not valid"
            
            date_today = date.today()
            data_date = date_today.replace(day=1,month=int(data[1]))
            data_date = datetime.strftime(data_date, "%Y-%m-%d")
            data_date = datetime.strptime(data_date, "%Y-%m-%d")
        except ValueError as e:
            return f"Incorrect input type, should be integer -> {str(e)}" 

        await LimitPlanController.add(data[0],data_date,data[2],detail)
      
        amount = "{:,}".format(int(data[2])).replace(",",".")
        return f"Planning to spend Rp {amount} for {data[2]} on {data_date}"

    async def get_monthly_limit_plan(data_date):
        next_month = data_date.replace(day=28) + timedelta(days=4)
        next_month =  next_month - timedelta(days=next_month.day)
        limit_plan = await LimitPlanController.get_monthly_limit_plan(data_date.replace(day=1),next_month)
        if limit_plan:
            date_converted = datetime.strftime(limit_plan[0].date_created, "%B")
            message = f"**MONTHLY OUTCOME ON {date_converted}**\n"
        else:
            return "There's no limit_plan on this month"
        date_data = ""
        for index, data in enumerate(limit_plan):
            if date_data != data.date_created:
                date_converted = datetime.strftime(data.date_created, "%d-%m-%Y")
                message += f"**{date_converted}**\n"
                date_data = data.date_created
              
            amount = "{:,}".format(data.amount).replace(",",".")
            message+= f"{index+1}. [**{data.category.name}**] {data.detail_item} Rp {amount}\n"

        return message

    async def get_limit_plan_total():
        limit_plan = await LimitPlanController.get_limit_plan_total()
        total = 0
        for i in limit_plan:
            if i.amount is None:
              break
            total += i.amount
        amount = "{:,}".format(total).replace(",",".")
        return total, amount