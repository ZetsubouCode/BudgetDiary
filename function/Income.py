from controller.Income import Income as IncomeController
from controller.Transaction import Transaction as TransactionController
class Income:
    async def add(msg:str):
        data = msg.split("-")
        transaction = await TransactionController.add()
        print(data)
        await IncomeController.add(transaction.id,data[0],data[1],data[2])
        return f"Success add {data[0]} to balance"

    async def get_saving():
        data = await IncomeController.get_saving()
        total = 0
        for i in data:
            total += i.amount
        return total
        
    async def get_detail_saving():
        income = await IncomeController.get_all()
        message = f"**Income**\n"
        for index,data in enumerate(income):
            message += f"{index+1}. Rp {data.amount} from {data.type}\n"

        return message

