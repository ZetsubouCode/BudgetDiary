import sys, time
from enum import Enum
from typing import Any

class Util:

	def get_current_strftime():
		return str(
			time.strftime("%H:%M:%S", time.localtime())
		)

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

		content = "[{}][{}][{}] {}".format(str(identifier), get_current_strftime(), str(debug_level), c)
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
