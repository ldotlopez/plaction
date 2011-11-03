from zizi.worker import Worker
import httplib

class unshort(Worker):
	def run(self, args, *kw):
		if args[0] != 'unshort':
			return

		url = args[1]
		resp = urllib.urlopen(url)
		print resp.info()
