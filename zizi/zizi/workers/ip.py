from zizi.worker import Worker
from zizi.messages import Message

import socket
import urllib

OWN_IP_ENDPOINT = 'http://cuarentaydos.com/ip.php'

class ip(Worker):
	def __init__(self, *args, **kwargs):
		Worker.__init__(self, *args, **kwargs)

	def run(self, args, **kwargs):
		if (len(args) != 2) or (args[0] != 'ip'):
			return None
	
		ret = None

		try:
			ip = args[1]
			if ip == 'own':
				fh = urllib.urlopen(OWN_IP_ENDPOINT)
				ret = ''.join(fh.readlines())
			else:
				ret = socket.gethostbyname(ip)
		except:
			pass

		if ret is not None:
			return Message(body = ret, final = True)

