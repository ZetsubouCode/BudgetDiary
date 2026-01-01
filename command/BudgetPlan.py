from controller.BudgetPlan import BudgetPlan as BudgetPlanController
from datetime import timedelta, date, datetime

class BudgetPlan:

  async def add(category_id: int, date_buy: date, detail: str, amount: int, quantity:int):

    budget_plan = await BudgetPlanController.add(category_id, date_buy, detail,
                                                 amount,quantity)
    month = datetime.strftime(date_buy,"%B %Y")
    amount = "{:,}".format(amount).replace(",", ".")
    if not budget_plan:
      return f"Failed to add budget plan"
    return f"Successfully add {detail} for **Rp {amount}** as much as **{quantity}** times in {month}"

  async def get_monthly_budget_plan(data_date):
    next_month = data_date.replace(day=28) + timedelta(days=4)
    next_month = next_month - timedelta(days=next_month.day)
    budget_plan = await BudgetPlanController.get_monthly_budget_plan(
      data_date.replace(day=1), next_month)
    if budget_plan:
      date_converted = datetime.strftime(budget_plan[0].date_buy, "%B")
      message = f"**MONTHLY BUDGET PLAN ON {date_converted}**\n"
    else:
      return "There's no budget plan on this month"
    date_data = ""
    total = 0
    for index, data in enumerate(budget_plan):
      if date_data != data.date_buy:
        date_converted = datetime.strftime(data.date_buy, "%d-%m-%Y")
        message += f"**{date_converted}**\n"
        date_data = data.date_buy
      if data.detail:
        detail = data.detail + " "
      else:
        detail = ""
      calculated_amount = data.amount*data.quantity
      total += calculated_amount
      amount = "{:,}".format(calculated_amount).replace(",", ".")
      message += f"{index+1}. [**{data.category.name}**] {detail}Rp {amount} on {data.date_buy}\n"
    total = "{:,}".format(total).replace(",", ".")
    message += f"\n**Total = Rp {total}**"

    return message

  async def get_monthly_total(date_input: date):
    next_month = date_input.replace(day=28) + timedelta(days=4)
    next_month = next_month - timedelta(days=next_month.day)
    budget_plan = await BudgetPlanController.get_monthly_total(
      date_input, next_month)
    return budget_plan[0].amount
