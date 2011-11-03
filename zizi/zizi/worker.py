from zizi.messages import Message

class Worker:
	def __init__(self):
		pass

	"""
	Returns a dict mapping actions with functions
	"""
	def map(self):
		return {}

	def execute(self, args):
		if len(args) == 0:
			return self.usage()

		m = self.map()
		(action, args) = (args[0], args[1:])

		if not m.has_key(action) or not callable(m[action]):
			args = [action] + args
			action = 'run'

		f = getattr(self, action)
		if action == 'run':
			cmd = args.pop(0)
			return f(cmd, args)
		else:
			return f(*args)

	def usage(self):
		return Message(body = "No help available")

	def run(self, args):
		return None

