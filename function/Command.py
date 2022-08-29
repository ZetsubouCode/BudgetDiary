from .Income import Income as IncomeFunction
class Command:

    async def help():
        data = "**List Commnad**\n>>> 1. !help\n2. !list_menu\n3. !add_category\n4. !add_outcome\n5. !add_income\n6. !get_daily_expense\n7. !get_monthly_expense\n8. !get_saving\n9. !get_detail_saving"
        return data

    async def list_menu():
        data = "menu list menu"
        return data

    async def add_category(client, message):

        def check(m):
            return m.channel == message.channel and m.author == message.author
        try:
            msg = await client.wait_for("message", check=check,timeout=60)
            
        except Exception as e:
            print(e)
            print("time out!")
        print(msg.content)

    async def add_income(client, message):

        def check(m):
            return m.channel == message.channel and m.author == message.author
        try:
            msg = await client.wait_for("message", check=check,timeout=60)
            
        except Exception as e:
            print(e)
            print("time out!")
        print(msg.content)
        message =await IncomeFunction.add(msg.content)
        return message