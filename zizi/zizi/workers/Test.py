from zizi.worker import Worker
from zizi.messages import Message
from zizi.decorators import accepts

class Test(Worker):
	def __init__(self, *args, **kw):
		Worker.__init__(self, *args, **kw)

	@accepts(object)
	def list(self):
		return "<empty list>"

	@accepts(object, int)
	def add(self, uri):
		return "URI %s added" % uri

	def map(self):
		return { 'list' : self.list, 'add' : self.add }

	def run(self, args):
		cmd = args.pop(0)

		assert(cmd in ('list', 'add'))

		ret = None
		if cmd == 'list':
			ret = self.list()

		elif cmd == 'add':
			ret = self.add(int(args[0]))

		else:
			return None

		if ret is not None:
			return Message(body = ret, final = True)

