from .Income import Income as IncomeFunction
from .Outcome import Outcome as OutcomeFunction
from .Category import Category as CategoryFunction
from .IncomeType import IncomeType as IncomeTypeFunction
from .LimitPlan import LimitPlan as LimitPlanFunction
from .Limit import Limit as LimitFunction
from .BudgetPlan import BudgetPlan as BudgetPlanFunction
from .SavingPlan import SavingPlan as SavingPlanFunction
from datetime import date,datetime
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
        \n11. !add_outcome_plan (development)
        \n12. !check_plan (development)
        \n13. !add_saving (development)
        \n14. !ars (development)'''
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
        \n8. Get Saving
        \nMerupakan menu untuk melihat uang yang dimiliki
        \n9. Get Detail Saving
        \nMerupakan menu untuk melihat list data pemasukkan
        \n10. Get Budget
        \nMerupakan menu untuk melihat sisa uang yang dimiliki
        \n11. Lorem ipsum
        \nRed fox fly Over a stick
        \n12. Lorem ipsum
        \nRed fox fly Over a stick
        \n13. Lorem ipsum
        \nRed fox fly Over a stick
        \n14. Lorem ipsum
        \nRed fox fly Over a stick
        '''
        return data

    async def get_income_type():
        return await IncomeTypeFunction.get_all_raw()

    async def get_category():
        return await CategoryFunction.get_all_raw()

    async def add_category(client, message):
        '''Menu 3'''
        input = "```Input example (name#emoticon[**optional**]) => steam wallet#:smile:```"
        await message.channel.send(input)
        message = await Command.get_input(client, message)
        response = await CategoryFunction.add(message.content)
        if response:
          m = f"Success add {message.content}"
        else:
          m = f"Failed to add Category"
        return m
    
    async def add_outcome(client, message):
        '''Menu 4'''
        category = await CategoryFunction.get_all()
        await message.channel.send(category)

        income_type = await IncomeTypeFunction.get_all()
        await message.channel.send(income_type)
        
        input = "```Input example (category_id#income_type_id#detail#amount#date[optional]) => 1#2#buy padang food#29000#30-08-2022```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await OutcomeFunction.add(message.content)
        return response
    
    async def add_income(client, message):
        '''Menu 5'''
        income_type = await IncomeTypeFunction.get_all()
        await message.channel.send(income_type)

        input = "```Input example (amount#income_type_id#detail[optional]#date[optional]) => 69420#CASH#NICE#30-08-2022```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await IncomeFunction.add(message.content)
        return response

    async def add_budget_plan(client, message):
        '''Menu 6'''
        income_type = await CategoryFunction.get_all()
        await message.channel.send(income_type)

        input = "```Input example (category_id#date_buy(DD-MM-YYYY)#amount#detail[optional]) => 1#30-08-2022#5000#beli cimol```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await BudgetPlanFunction.add(message.content)
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
        income_type = await IncomeTypeFunction.get_all()
        await message.channel.send(income_type)

        input = "```Input example (category_id#month_saving(M)#amount) => 1#8#5000```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await SavingPlanFunction.add(message.content)
        return response

    async def add_limit_plan(client, message):
        '''Menu 8'''
        income_type = await IncomeTypeFunction.get_all()
        await message.channel.send(income_type)

        input = "```Input example (amount#income_type_id#detail[optional]#date[optional]) => 69420#CASH#NICE#30-08-2022```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await LimitPlanFunction.add(message.content)
        return response
    
    async def get_daily_outcome(client, message):
        '''Menu 9'''
        input ="```Input example (dd-mm-yyyy) => 15-10-2022```\nInput date :"
        await message.channel.send(input)
        data = await Command.get_input(client, message)
        input_date = datetime.strptime(data.content,"%d-%m-%Y")
        input_date = datetime.strftime(input_date, "%Y-%m-%d")
        response = await OutcomeFunction.get_daily_outcome(input_date)
        return response
        
    async def get_monthly_outcome(client, message):
        '''Menu 10'''
        input ="```Input example (1~12) => 5```\nInput date month :"
        await message.channel.send(input)
        data = await Command.get_input(client, message)
        if int(data.content) > 12 or int(data.content) < 1:
          return f"Please input correctly. {data.content} is not valid"
          
        date_today = date.today()
        input_date = date_today.replace(day=1,month=int(data.content))
        input_date = datetime.strftime(input_date, "%Y-%m-%d")
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
        response = await OutcomeFunction.get_monthly_outcome(input_date)
        return response

    async def get_outcome_report(client, message):
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
        
    async def get_daily_income(client, message):
        '''Menu 11'''
        input = f"**Current Money**\n"
        await message.channel.send(input)
        response, formatting = await IncomeFunction.get_daily_income()
        return f"Rp {formatting}"
    
    async def get_monthly_income(client, message):
        '''Menu 12'''
        input ="```Input example (1~12) => 5```\nInput date month :"
        await message.channel.send(input)
        data = await Command.get_input(client, message)
        if int(data.content) > 12 or int(data.content) < 1:
          return f"Please input correctly. {data.content} is not valid"
          
        date_today = date.today()
        input_date = date_today.replace(day=1,month=int(data.content))
        input_date = datetime.strftime(input_date, "%Y-%m-%d")
        input_date = datetime.strptime(input_date, "%Y-%m-%d")
      
        input = f"**Detail saving**\n"
        await message.channel.send(input)
        response = await IncomeFunction.get_monthly_income(input_date)
        return response

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

    async def transfer(client, message):
        '''Menu 5'''
        income_type = await IncomeTypeFunction.get_all()
        await message.channel.send(income_type)

        input = "```Input example (id_source#amount#id_destination) => 1#69420#5```"
        await message.channel.send(input)

        message = await Command.get_input(client, message)
        response =await IncomeFunction.transfer(message.content)
        return response
        
    