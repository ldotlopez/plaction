from zizi.worker import Worker

class WorkerA(Worker):
	def __init__(self):
		Worker.__init__(self)
		print "Worker A init"

	def do(self):
		print "Worker A do"
