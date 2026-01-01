from controller.Limit import Limit as LimitController
class Limit:
    async def add(name):
        '''@param name = the name of the income_type'''
        await LimitController.add(name)

    async def get_all():
        income_type = await LimitController.get_all()
        message = "**LIST LIMIT\n**"
        for data in income_type:
            message += f"{data.id}. {data.name}\n"
        return message