from zizi.worker import Worker

class WorkerB(Worker):
	def __init__(self):
		Worker.__init__(self)
		print "Worker B init"

	def do(self):
		print "Worker B do"
