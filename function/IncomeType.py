from controller.IncomeType import IncomeType as IncomeTypeController
from util import Util

class IncomeType:
    main_endpoint = "income_type"
    
    async def add(name:str):
        '''@param name = the name of the income_type'''
        sub_endpoint = "add"
        form_data = {
        "name":name
        }
        income_type = Util.send_request('POST',main_endpoint,sub_endpoint,data=form_data)

    async def get_all():
        income_type = await get_all_raw()
        message = "**LIST INCOME TYPE\n**"
        for idx,data in enumerate(income_type):
            message += f"{idx}. {data.name}\n"
        return message

    async def get_all_raw():
        sub_endpoint = "all"
        income_type = Util.send_request('GET',main_endpoint,sub_endpoint)
        return income_type.content
