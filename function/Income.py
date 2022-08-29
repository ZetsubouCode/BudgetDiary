from controller.Income import Income as IncomeController
from controller.Transaction import Transaction as TransactionController
class Income:
    async def add(msg:str):
        data = msg.split(";")
        transaction = await TransactionController.add(None,None)
        print(data)
        await IncomeController.add(transaction.id,data[0],data[1],data[2])
        return "success"