import itertools
from nextcord import Embed, Color
# from .Income import Income as IncomeFunction
# from .Outcome import Outcome as OutcomeFunction
from .Category import Category as CategoryFunction
# from .LimitPlan import LimitPlan as LimitPlanFunction
# from .Limit import Limit as LimitFunction
# from .BudgetPlan import BudgetPlan as BudgetPlanFunction
# from .SavingPlan import SavingPlan as SavingPlanFunction
from datetime import date, datetime

class Command:

  async def get_input(client, message, condition=True):
    '''Tool function untuk mengambil inputan user'''

    def check(m):
      return m.channel == message.channel and m.author == message.author and condition

    try:
      msg = await client.wait_for("message", check=check, timeout=360)

    except Exception as e:
      print(e)
      print("time out!")
      return "Time out!"
    return msg

  async def help():
    '''Menu 1'''
    data = '''**List Command**
        \n>>> 1. !help
        \n2. !menu
        \n3. !add_category
        \n4. !add_outcome
        \n5. !add_income
        \n6. !daily_outcome
        \n7. !monthly_outcome
        \n8. !daily_income
        \n9. !monthly_income
        \n10. !budget
        \n11. !detail_budget
        \n11. !add_outcome_plan (development)
        \n12. !check_plan (development)
        \n13. !add_saving (development)
        \n14. !ars (development)
        \n15. !transfer'''
    return data

  async def list_menu():
    '''Menu 2'''
    embed = Embed(
      title="Menu Utama",
      description="Ringkasan fitur BudgetDiary. Gunakan `/help` untuk detail. Perintah bertanda [PIN] memerlukan PIN.",
      color=Color.blue(),
    )
    embed.add_field(
      name="Akun dan Bantuan",
      value=(
        "`/register` Buat akun dan PIN\n"
        "`/pin_remember` [PIN] Atur ingat PIN sementara\n"
        "`/help` Ringkasan perintah\n"
        "`/menu` Penjelasan singkat tiap menu"
      ),
      inline=False,
    )
    embed.add_field(
      name="Kategori",
      value=(
        "`/list_categories` Lihat kategori income atau outcome\n"
        "`/add_category` [PIN] Tambah kategori baru\n"
        "`/edit_category` [PIN] Ubah nama atau emoticon kategori\n"
        "`/delete_category` [PIN] Hapus kategori yang tidak dipakai"
      ),
      inline=False,
    )
    embed.add_field(
      name="Transaksi",
      value=(
        "`/add_income` [PIN] Catat pemasukan\n"
        "`/add_outcome` [PIN] Catat pengeluaran\n"
        "`/delete_income` [PIN] Hapus transaksi pemasukan\n"
        "`/transfer_income` Pindahkan saldo antar kategori income\n"
        "`/transfer` Pindahkan saldo antar kategori income"
      ),
      inline=False,
    )
    embed.add_field(
      name="Laporan",
      value=(
        "`/get_daily_income` Laporan pemasukan harian\n"
        "`/get_monthly_income` Laporan pemasukan bulanan\n"
        "`/get_yearly_income` Laporan pemasukan tahunan\n"
        "`/get_daily_outcome` Laporan pengeluaran harian\n"
        "`/get_monthly_outcome` Laporan pengeluaran bulanan\n"
        "`/get_yearly_outcome` Laporan pengeluaran tahunan\n"
        "`/monthly_summary` Ringkasan pemasukan dan pengeluaran bulanan\n"
        "`/outcome_insight` Insight pengeluaran (kategori terboros & transaksi termahal)"
      ),
      inline=False,
    )
    embed.add_field(
      name="Format Tanggal",
      value="Harian: `DD-MM-YYYY` | Bulanan: `MM-YYYY` | Tahunan: `YYYY`",
      inline=False,
    )
    return embed

  # def get_income_type():
  #   return IncomeTypeFunction.get_all_raw()

  # def get_category():
  #   return CategoryFunction.get_all_raw()

  async def add_category(name: str, emoticon: str, type:str = "income"):
    '''Menu 3'''
    response = await CategoryFunction.add(name, emoticon,type)
    if response:
      # temp_db._category = CategoryFunction.get_all_raw()
      m = f"Success add {name} {emoticon}"
    else:
      m = f"Failed to add Category"
    return m

  # async def add_outcome(outcome_type: int, income_type: int, amount: int,
  #                       detail: str, date: str):
  #   '''Menu 4'''
  #   response = await OutcomeFunction.add(outcome_type, income_type, amount,
  #                                        detail, date)
  #   return response

  # async def add_income(income_type: int, amount: int, detail: str, date: date):
  #   '''Menu 5'''
  #   response = await IncomeFunction.add(income_type, amount, detail, date)
  #   return response

  # async def add_budget_plan(category_id: int, date_buy: str, detail: str,
  #                           amount: int, quantity: int):
  #   '''Menu 6'''
  #   date_buy = datetime.strptime(date_buy,"%d-%m-%Y")
  #   response = await BudgetPlanFunction.add(category_id,date_buy,detail,amount,quantity)
  #   return response

  # async def get_monthly_budget_plan(month):
  #   '''Menu 7'''
  #   if int(month) > 12 or int(month) < 1:
  #     return f"Please input correctly. {month} is not valid"

  #   date_today = date.today()
  #   input_date = date_today.replace(day=1, month=int(month))
  #   input_date = datetime.strftime(input_date, "%Y-%m-%d")
  #   input_date = datetime.strptime(input_date, "%Y-%m-%d")
  #   response = await BudgetPlanFunction.get_monthly_budget_plan(input_date)
  #   return response

  # async def add_saving_plan(client, message):
  #   '''Menu 7'''
  #   income_type = temp_db._income_type
  #   await message.channel.send(income_type)

  #   input = "```Input example (category_id#month_saving(M)#amount) => 1#8#5000```"
  #   await message.channel.send(input)

  #   message = await Command.get_input(client, message)
  #   response = await SavingPlanFunction.add(message.content)
  #   return response

  # async def get_daily_outcome(date: str):
  #   '''Menu 9'''
  #   response = await OutcomeFunction.get_daily_outcome(date)
  #   return response

  # async def get_monthly_outcome(month: int):
  #   '''Menu 10'''
  #   if int(month) > 12 or int(month) < 1:
  #     return f"Please input correctly. {month} is not valid"

  #   date_today = date.today()
  #   input_date = date_today.replace(day=1, month=int(month))
  #   input_date = datetime.strftime(input_date, "%Y-%m-%d")
  #   input_date = datetime.strptime(input_date, "%Y-%m-%d")
  #   # response = await OutcomeFunction.get_monthly_outcome(input_date)
  #   title, response = await OutcomeFunction.get_monthly_outcome_json(input_date
  #                                                                    )
  #   return title, response

  # async def get_outcome_report(month: int):
  #   '''Menu 7'''
  #   if int(month) > 12 or int(month) < 1:
  #     return f"Please input correctly. {month} is not valid"

  #   date_today = date.today()
  #   input_date = date_today.replace(day=1, month=int(month))
  #   input_date = datetime.strftime(input_date, "%Y-%m-%d")
  #   input_date = datetime.strptime(input_date, "%Y-%m-%d")
  #   format_date = datetime.strftime(input_date, "%B %Y")
  #   budget_plan = await BudgetPlanFunction.get_monthly_total(input_date)
  #   if budget_plan is None:
  #     return f"There is no budget plan for {format_date}"
  #   outcome = await OutcomeFunction.get_monthly_total(input_date)
  #   different = budget_plan - outcome
  #   diff_format = "{:,}".format(abs(different)).replace(",", ".")
  #   if different < 0:
  #     message = f"Outcome on {format_date} is too much. Rp {diff_format} more was spend on this month"
  #   else:
  #     message = f"Outcome on {format_date} is on budget. Rp {diff_format} was saved on this month"
  #   return message

  # async def get_daily_income(date):
  #   '''Menu 11'''
  #   response = await IncomeFunction.get_daily_income(date)
  #   return response

  # async def get_monthly_income(month: int):
  #   '''Menu 12'''
  #   if int(month) > 12 or int(month) < 1:
  #     return f"Please input correctly. {month} is not valid"

  #   date_today = date.today()
  #   input_date = date_today.replace(day=1, month=int(month))
  #   input_date = datetime.strftime(input_date, "%Y-%m-%d")
  #   input_date = datetime.strptime(input_date, "%Y-%m-%d")

  #   header = f"**Detail income**\n"
  #   response = await IncomeFunction.get_monthly_income(input_date)
  #   return header + response

  # async def get_remaining_money(client, message):
  #   '''Menu 13'''
  #   input = f"**Remaining Money**\n"
  #   await message.channel.send(input)
  #   saving, formatting = await IncomeFunction.get_saving()
  #   outcome, formatting = await OutcomeFunction.get_outcome()
  #   total = "{:,}".format(saving - outcome).replace(",", ".")
  #   return f"Rp {total}"

  # async def this_month_budget(client, message):
  #   '''Menu 14'''
  #   data = date.today()
  #   input = f"**This Month Budget**\n"
  #   await message.channel.send(input)
  #   saving = await IncomeFunction.get_last_saving()
  #   outcome, formatting = await OutcomeFunction.get_outcome()
  #   remaining = saving - outcome
  #   response = await IncomeFunction.get_monthly_income(data, remaining)
  #   return response

  # async def transfer(source, amount, target, data_date):
  #   '''Menu 5'''
  #   if date:
  #     data_date = datetime.strptime(data_date, "%d-%m-%Y")
  #   else:
  #     data_date = date.today()
  #   response = await IncomeFunction.transfer(source, amount, target, data_date)
  #   return response

  # async def detail_budget():
  #   '''Menu X'''
  #   msg1, income = await IncomeFunction.get_group_income()
  #   msg2, outcome = await OutcomeFunction.get_group_outcome()
  #   if not income or not outcome:
  #     return "Income or Outcome not found"
  #   final_data = []
  #   for index, data in enumerate(income):
  #     match = False
  #     for index2, data_o in enumerate(outcome):
  #       if data.name == data_o.name:
  #         amount = data.amount - data_o.amount
  #         final_data.append((amount, data.name))
  #         match = True
  #     if not match:
  #       final_data.append((data.amount, data.name))

  #   msg1 = "**INCOME**\n" + msg1
  #   msg2 = "**OUTCOME**\n" + msg2
  #   msg3 = "**REMAIN MONEY**\n"
  #   index = 0

  #   for index, (amount, name) in enumerate(final_data):
  #     amount = "{:,}".format(amount).replace(",", ".")
  #     msg3 += f"{index+1}. Rp {amount} from {name}\n"
  #   return msg1 + "\n" + msg2 + "\n" + msg3

  # async def group_outcome():
  #   '''Menu X'''
  #   message, outcome = await OutcomeFunction.get_group_outcome()
  #   return message

  # async def get_specific_latest_outcome(keyword, category_id):
  #   '''Menu X'''
  #   data = await OutcomeFunction.get_specific_latest_outcome(
  #     keyword, category_id)
  #   if data:
  #     if data.category.emoticon is not None:
  #       emot = f"{data.category.emoticon}"
  #     else:
  #       emot = f"[{data.category.name}]"
  #     date_converted = datetime.strftime(data.date_created, "%A, %d-%B-%Y")
  #     amount_converted = f'{data.amount:,}'.replace(",", ".")
  #     return f"{emot} Spent Rp {amount_converted} for {data.detail_item} using {data.income_type.name} at {date_converted} "
  #   else:
  #     return f"There's no data available for keyword {keyword}"
