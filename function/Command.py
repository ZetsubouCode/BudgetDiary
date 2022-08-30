from .Income import Income as IncomeFunction
from .Outcome import Outcome as OutcomeFunction
from .Category import Category as CategoryFunction
from datetime import date
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
        return msg

    async def help():
        '''Menu 1'''
        data = '''**List Command**
        \n>>> 1. !help
        \n2. !list_menu
        \n3. !add_category
        \n4. !add_outcome
        \n5. !add_income
        \n6. !get_daily_expense
        \n7. !get_monthly_expense
        \n8. !get_saving
        \n9. !get_detail_saving
        \n10. !get_remaining_money
        \n11. !this_month_budget'''
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
        \n6. Get Daily Expense
        \nMerupakan menu untuk melihat data pengeluaran harian
        \n7. Get Monthly Expense
        \nMerupakan menu untuk melihat data pengeluaran bulanan
        \n8. Get Saving
        \nMerupakan menu untuk melihat uang yang dimiliki
        \n9. Get Detail Saving
        \nMerupakan menu untuk melihat list data pemasukkan
        \n10. Get Remaining Money
        \nMerupakan menu untuk melihat sisa uang yang dimiliki
        \n11. This Month Budget
        \nMerupakan menu untuk melihat budget yang dimiliki pada bulan ini'''
        return data

    async def add_category(client, message):
        '''Menu 3'''
        input = "```Input example (name) => steam wallet```"
        await message.channel.send(input)
        message = await Command.get_input(client, message)
        response =await IncomeFunction.add(message.content)
        return response
    
    async def add_outcome(client, message):
        '''Menu 4'''
        input = "```Input example (category_id-detail-amount) => 1-buy padang food-29000```"
        category = await CategoryFunction.get_all()
        await message.channel.send(category)
        await message.channel.send(input)
        message = await Command.get_input(client, message)
        response =await OutcomeFunction.add(message.content)
        return response
    
    async def add_income(client, message):
        '''Menu 5'''
        input = "```Input example (amount-type name-detail if any) => 69420-CASH-NICE```"
        type = '''**INCOME LIST TYPE**
        \n1. BANK BCA
        \n2. BANK ALADIN
        \n3. GIFT
        \n4. CASH
        \n5. GOPAY
        \n6. OVO
        \n7. SHOPEE PAY
        '''
        await message.channel.send(type)
        await message.channel.send(input)
        message = await Command.get_input(client, message)
        response =await IncomeFunction.add(message.content)
        return response
    
    async def get_daily_expense(client, message):
        '''Menu 6'''
        input ="```Input example (yyyy-mm-dd) => 2022-10-15```\nInput date :"
        await message.channel.send(input)
        data = await Command.get_input(client, message)
        response = await OutcomeFunction.get_daily_expense(data.content)
        return response
        
    async def get_monthly_expense(client, message):
        '''Menu 7'''
        data = date.today()
        input = f"Today date is {data}"
        await message.channel.send(input)
        response = await OutcomeFunction.get_monthly_expense(data)
        return response
        
    async def get_saving(client, message):
        '''Menu 8'''
        input = f"**Current Money**\n"
        await message.channel.send(input)
        response = await IncomeFunction.get_saving()
        return f"Rp {response}"
    
    async def get_detail_saving(client, message):
        '''Menu 9'''
        input = f"**Detail saving**\n"
        await message.channel.send(input)
        response = await IncomeFunction.get_detail_saving()
        return response

    async def get_remaining_money(client, message):
        '''Menu 10'''
        input = f"**Remaining Money**\n"
        await message.channel.send(input)
        saving = await IncomeFunction.get_saving()
        expense = await OutcomeFunction.get_expense()
        return f"Rp {saving-expense}"

    async def this_month_budget(client, message):
        '''Menu 11'''
        input = f"**This Month Budget**\n"
        await message.channel.send(input)
        response = await IncomeFunction.get_saving()
        return f"Rp {response}"
    