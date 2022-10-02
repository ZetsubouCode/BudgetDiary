from .Income import Income as IncomeFunction
from .Outcome import Outcome as OutcomeFunction
from .Category import Category as CategoryFunction
from .IncomeType import IncomeType as IncomeTypeFunction
from .LimitPlan import LimitPlan as LimitPlanFunction
from .Limit import Limit as LimitFunction
from .BudgetPlan import BudgetPlan as BudgetPlanFunction
from .SavingPlan import SavingPlan as SavingPlanFunction
from datetime import date,datetime
from temp_db import temp_db
class Command:

    async def get_input(client, message, condition=True):
        '''Tool function untuk mengambil inputan user'''
        def check(m):
            return m.channel == message.channel and m.author == message.author and condition
        try:
            msg = await client.wait_for("message", check=check,timeout=360)
            
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
        data = '''
        **List Menu**
        \n>>> 1. Help
        \nMerupakan menu untuk melihat list command yang tersedia
        \n2. List Menu
        \nMerupakan menu untuk melihat penjelasan singkat akan menu yang tersedia
        \n3. Add Category
        \nMerupakan menu untuk menambah data kategori pengeluaran
        \n4. Add Outcome
        \nMerupakan menu untuk menambah data pengeluaran
        \n5. Add Income
        \nMerupakan menu untuk menambah data pemasukkan
        \n6. Get Daily Outcome
        \nMerupakan menu untuk melihat data pengeluaran harian
        \n7. Get Monthly Outcome
        \nMerupakan menu untuk melihat data pengeluaran bulanan
        \n8. Get Daily Income
        \nMerupakan menu untuk melihat uang yang dimiliki
        \n9. Get Monthly Income
        \nMerupakan menu untuk melihat list data pemasukkan
        \n10. Get Budget
        \nMerupakan menu untuk melihat sisa uang yang dimiliki
        \n11. Get List Budget
        \nRed fox fly Over a stick
        \n12. Lorem ipsum
        \nRed fox fly Over a stick
        \n13. Lorem ipsum
        \nRed fox fly Over a stick
        \n14. Lorem ipsum
        \nRed fox fly Over a stick
        \n15. Lorem ipsum
        \nRed fox fly Over a stick
        '''
        return data

    def get_income_type():
        return IncomeTypeFunction.get_all_raw()

    def get_category():
        return CategoryFunction.get_all_raw()

    async def add_category(name:str, emoticon:str):
        '''Menu 3'''
        response = await CategoryFunction.add(name, emoticon)
        if response:
          temp_db._category = CategoryFunction.get_all_raw()
          m = f"Success add {name} :{emoticon}:"
        else:
          m = f"Failed to add Category"
        return m
    
    async def add_outcome(outcome_type:int,income_type:int,amount:int,detail:str,date:str):
        '''Menu 4'''
        response =await OutcomeFunction.add(outcome_type,income_type,amount,detail,date)
        return response
    
    async def add_income(income_type,amount,detail,date):
        '''Menu 5'''
        response = await IncomeFunction.add(income_type,amount,detail,date)
        return response

    async def add_budget_plan(client, message):
        '''Menu 6'''
        income_type = await IncomeTypeFunction.get_all_temp()
        await message.channel.send(income_type)

        input = "```Input example (category_id#date_buy(DD-MM-YYYY)#amount#detail[optional]) => 1#30-08-2022#5000#beli cimol```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response = await BudgetPlanFunction.add(message.content)
        return response

    async def get_monthly_budget_plan(client, message):
        '''Menu 7'''
        input ="```Input example (1~12) => 5```\nInput date month :"
        await message.channel.send(input)
        data = await Command.get_input(client, message)
        if int(data.content) > 12 or int(data.content) < 1:
          return f"Please input correctly. {data.content} is not valid"
          
        date_today = date.today()
        input_date = date_today.replace(day=1,month=int(data.content))
        input_date = datetime.strftime(input_date, "%Y-%m-%d")
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
        response = await BudgetPlanFunction.get_monthly_budget_plan(input_date)
        return response

    async def add_saving_plan(client, message):
        '''Menu 7'''
        income_type = temp_db._income_type
        await message.channel.send(income_type)

        input = "```Input example (category_id#month_saving(M)#amount) => 1#8#5000```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await SavingPlanFunction.add(message.content)
        return response

    async def add_limit_plan(client, message):
        '''Menu 8'''
        income_type = await IncomeTypeFunction.get_all_temp()
        await message.channel.send(income_type)

        input = "```Input example (amount#income_type_id#detail[optional]#date[optional]) => 69420#CASH#NICE#30-08-2022```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await LimitPlanFunction.add(message.content)
        return response
    
    async def get_daily_outcome(date:str):
        '''Menu 9'''
        response = await OutcomeFunction.get_daily_outcome(date)
        return response
        
    async def get_monthly_outcome(month):
        '''Menu 10'''
        if int(month) > 12 or int(month) < 1:
          return f"Please input correctly. {month} is not valid"
          
        date_today = date.today()
        input_date = date_today.replace(day=1,month=int(month))
        input_date = datetime.strftime(input_date, "%Y-%m-%d")
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
        # response = await OutcomeFunction.get_monthly_outcome(input_date)
        title, response = await OutcomeFunction.get_monthly_outcome_json(input_date)
        return title,response

    async def get_outcome_report(month):
        '''Menu 7'''
        if int(month) > 12 or int(month) < 1:
          return f"Please input correctly. {month} is not valid"
          
        date_today = date.today()
        input_date = date_today.replace(day=1,month=int(month))
        input_date = datetime.strftime(input_date, "%Y-%m-%d")
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
        format_date = datetime.strftime(input_date, "%B %Y")
        budget_plan = await BudgetPlanFunction.get_monthly_total(input_date)
        if budget_plan is None:
            return f"There is no budget plan for {format_date}"
        outcome = await OutcomeFunction.get_monthly_total(input_date)
        different = budget_plan-outcome
        diff_format = "{:,}".format(abs(different)).replace(",",".")
        if different < 0:
            message = f"Outcome on {format_date} is too much. Rp {diff_format} more was spend on this month"
        else:
            message = f"Outcome on {format_date} is on budget. Rp {diff_format} was saved on this month"
        return message
        
    async def get_daily_income(date):
        '''Menu 11'''
        response = await IncomeFunction.get_daily_income(date)
        return response
    
    async def get_monthly_income(month):
        '''Menu 12'''
        if int(month) > 12 or int(month) < 1:
          return f"Please input correctly. {month} is not valid"
          
        date_today = date.today()
        input_date = date_today.replace(day=1,month=int(month))
        input_date = datetime.strftime(input_date, "%Y-%m-%d")
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
      
        header = f"**Detail income**\n"
        response = await IncomeFunction.get_monthly_income(input_date)
        return header+response

    async def get_remaining_money(client, message):
        '''Menu 13'''
        input = f"**Remaining Money**\n"
        await message.channel.send(input)
        saving, formatting = await IncomeFunction.get_saving()
        outcome, formatting = await OutcomeFunction.get_outcome()
        total = "{:,}".format(saving-outcome).replace(",",".")
        return f"Rp {total}"

    async def this_month_budget(client, message):
        '''Menu 14'''
        data = date.today()
        input = f"**This Month Budget**\n"
        await message.channel.send(input)
        saving = await IncomeFunction.get_last_saving()
        outcome, formatting = await OutcomeFunction.get_outcome()
        remaining = saving - outcome
        response = await IncomeFunction.get_monthly_income(data, remaining)
        return response

    async def transfer(source,amount,target):
        '''Menu 5'''
        response =await IncomeFunction.transfer(source,amount,target)
        return response

    async def detail_budget():
      '''Menu X'''
      msg1, income = await IncomeFunction.get_group_income()
      msg2, outcome =  await OutcomeFunction.get_group_outcome()
      final_data=[]
      index=0
      for data in income:
        if data.name == outcome[index].name:
          amount = data.amount - outcome[index].amount
          final_data.append((amount,data.name))
          index+=1
        else :
          final_data.append((data.amount,data.name))
          
      msg1="**INCOME**\n"+msg1
      msg2="**OUTCOME**\n"+msg2
      msg3="**REMAIN MONEY**\n"
      index=0
      
      for amount,name in final_data:
        amount = "{:,}".format(amount).replace(",", ".")
        msg3 += f"{index+1}. Rp {amount} from {name}\n"
        index+=1
      return msg1+"\n"+msg2+"\n"+msg3

    async def group_outcome(client, message):
      '''Menu X'''
      return await OutcomeFunction.get_group_outcome()
      
        
    