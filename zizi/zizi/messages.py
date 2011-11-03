class Message:
	_keys = ('body', 'final')
	
	def __init__(self, body, final = False):
		self.body  = body
		self.final = final

