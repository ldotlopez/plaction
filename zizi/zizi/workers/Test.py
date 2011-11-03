from zizi.worker import Worker
from zizi.messages import Message
from zizi.decorators import accepts

class Test(Worker):
	def __init__(self, *args, **kw):
		Worker.__init__(self, *args, **kw)

	def usage(self):
		return Message(body = """
			Usage:
			list    -> List current torrent list
			add uri -> Adds an URI to transmission and starts it
			""")

	"""
	list current torrents
	"""
	@accepts(object)
	def list(self):
		return Message(body = "<empty list>")

	"""
	Adds an URI to transmission
	"""
	@accepts(object, int)
	def add(self, uri):
		return Message(body = "URI %s added" % uri)

	def amap(self):
		return { 'list' : self.list, 'add' : self.add }

	def run(self, cmd, args):
		#cmd = args.pop(0)

		if not cmd in ('list', 'add'):
			return self.usage()

		msg = None
		if cmd == 'list':
			msg = self.list()

		elif cmd == 'add':
			try:
				msg = self.add(int(args[0]))
			except (IndexError, TypeError, ValueError) as e:
				return self.usage()

		else:
			return None

		if msg is not None:
			return msg

