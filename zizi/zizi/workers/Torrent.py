from zizi.worker import Worker
from zizi.messages import Message

class Torrent(Worker):
	def __init__(self, *args, **kw):
		Worker.__init__(self, *args, **kw)

	def list(self):
		return "<empty list>"

	def add(self, uri):
		return "URI %s added" % uri

	def run(self, args,**kw):
		cmd = None
		try:
			cmd = args[1]
		except IndexError:
			return None

		ret = None
		if cmd == 'list':
			ret = self.list()

		elif cmd == 'add':
			try:
				uri = args[2]
			except IndexError:
				return None
			ret = self.add(uri)
		else:
			return None

		if ret is not None:
			return Message(body = ret, final = True)

