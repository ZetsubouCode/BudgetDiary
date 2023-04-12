import sys, time, requests
from enum import Enum
from typing import Any
from datetime import datetime, timedelta, date
from __env import ENV

class Util:

    def get_current_strftime():
        return str(
            time.strftime("%H:%M:%S", time.localtime())
        )
    
    def date_validation(input_date):
        if input_date:
            try:
                data_date = datetime.strptime(input_date, "%d-%m-%Y")
                data_date = datetime.strftime(data_date, "%Y-%m-%d")
            except ValueError as e:
                return f"Incorrect data format, should be DD-MM-YYYY -> {str(e)}"
        else:
            data_date = date.today()
        return data_date

    def get_first_and_last_day(date_input):
        date_converted_a = date_input.replace(day=1)
        next_month = date_input.replace(day=28) + timedelta(days=4)
        next_month = next_month - timedelta(days=next_month.day)
        date_converted_b = next_month
        return date_converted_a, date_converted_b
    
    def send_request(method:str, main_endpoint:str, sub_endpoint:str, headers=None, data=None, json=None):
        url = f"{ENV.HOST}/{main_endpoint}/{sub_endpoint}"
        
        response = requests.request(method, url, headers=headers, data=data, json=json)

        # Raise an exception if the response indicates an error
        response.raise_for_status()

        # Parse the response JSON and return it as a dictionary
        print(str(response.json()))
        return response.json()

class DebugLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class __Debug:
    def __init__(self):
        ...

    def msg(self, identifier: str, content: Any, debug_level: DebugLevel = DebugLevel.INFO):
        c = None
        try:
            c = str(content)
        except:
            try:
                c = repr(content)
            except:
                ...

        content = "[{}][{}][{}] {}".format(str(identifier), Util.get_current_strftime(), str(debug_level), c)
        if (debug_level == DebugLevel.INFO) or (debug_level == DebugLevel.WARNING):
            print(content, file=sys.stdout)
        else:
            print(content, file=sys.stderr)

    def info(self, identifier: str, content: Any):
        self.msg(identifier, content, DebugLevel.INFO)

    def warning(self, identifier: str, content: Any):
        self.msg(identifier, content, DebugLevel.WARNING)

    def error(self, identifier: str, content: Any):
        self.msg(identifier, content, DebugLevel.ERROR)

    def critical(self, identifier: str, content: Any):
        self.msg(identifier, content, DebugLevel.CRITICAL)


Debug = __Debug()
