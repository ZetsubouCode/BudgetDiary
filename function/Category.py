from controller.Category import Category as CategoryController
class Category:
    async def add(name):
        '''@param name = the name of the category'''
        await CategoryController.add(name)

    async def get_all():
        category = await CategoryController.get_all()
        message = "**LIST CATEGORY\n**"
        for data in category:
            message += f"{data.id}. {data.name}\n"
        return message
