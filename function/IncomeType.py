from controller.IncomeType import IncomeType as IncomeTypeController
class IncomeType:
    async def add(name):
        '''@param name = the name of the income_type'''
        await IncomeTypeController.add(name)

    async def get_all():
        income_type = await IncomeTypeController.get_all()
        message = "**LIST INCOME TYPE\n**"
        for data in income_type:
            message += f"{data.id}. {data.name}\n"
        return message

    async def get_all_raw():
        return await IncomeTypeController.get_all()