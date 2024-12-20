import sys, time, json
from enum import Enum
from typing import Any
from datetime import datetime, timedelta, date

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
    
    def read_json(JSON_FILE_PATH=""):
        try:
            with open(JSON_FILE_PATH, 'r') as file:
                return json.load(file)
        except FileNotFoundError:
            return {}

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
