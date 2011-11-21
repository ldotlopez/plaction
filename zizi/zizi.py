#!/usr/bin/env python

import zizi
import zizi.workers
from zizi.messages import Message
import sys
import os

def _(s):
	return s

class Zizi:
	INFO  = 0
	WARN  = 1
	ERROR = 2

	class InvalidAction(StandardError): pass
	class NotImplemented(StandardError): pass
	class InvalidArgumentCount(StandardError): pass
	class WorkerLoadException(StandardError): pass

	def __init__(self, load_mods):
		self._workers = []
		self._workers_map = {}

		if len(load_mods) == 0:
			load_mods =  [ x[:-3] for x in os.listdir(zizi.workers.__path__[0]) if x.endswith('.py') and not x.startswith('__') ]

		for worker_name in load_mods:
			try:
				self._load_worker(worker_name)
				self.log(Zizi.INFO, _("Loaded worker %s") % worker_name)
			except Zizi.WorkerLoadException as e:
				self.log(Zizi.WARN, _("Unable to load worker %s: %s") % (worker_name, e))

	def log(self, level = INFO, msg = None):
		m = { Zizi.INFO : 'INFO', Zizi.WARN : 'WARN', Zizi.ERROR : 'ERROR' }
		print "[%s] %s" % (m[level], msg)

	def _load_worker(self, worker_name):
		try:
			m = __import__('zizi.workers.' + worker_name)
			worker_m = getattr(m.workers, worker_name)
			worker_class = getattr(worker_m, worker_name)
			worker = worker_class()
		except ImportError as e:
			raise Zizi.WorkerLoadException, _("module doesn't exists")
		except AttributeError as e:
			raise Zizi.WorkerLoadException, _("module doesn't implement class %s" % worker_name)

		self._workers.append(worker)
		self._workers_map[worker_name] = worker

	def execute(self, args):
		if len(args) < 1:
			raise Zizi.InvalidArgumentCount

		worker_name = args.pop(0)

		try:
			worker = self._workers_map[worker_name]
		except KeyError:
			raise Zizi.NotImplemented, _("worker not available")
		else:
			return worker.execute(args)

	def get_global_usage(self):
		ret = dict()
		for (name,worker) in self._workers_map.iteritems():
			ret[name] = worker.usage().body
		return ret

if __name__ == '__main__':
	z = Zizi([])
	try:
		msg = z.execute(sys.argv[1:])
	except Zizi.InvalidArgumentCount:
		for (mod, usage) in z.get_global_usage().iteritems():
			print "Module %s:" % mod
			print "----------"
			print usage
			print
		sys.exit(1)

	if msg is not None:
		print "Result: %s" % msg.body
	sys.exit(0)

	workers = []
	workers_map = {}

	for worker_name in load_mods:
		m = __import__('zizi.workers.' + worker_name)
		worker_m = getattr(m.workers, worker_name)
		worker_class =getattr(worker_m, worker_name)
		worker = worker_class()
		workers.append(worker)
		workers_map[worker_name] = worker

	# sys.exit(0)

	if workers_map.has_key(sys.argv[1]):
		w = workers_map[sys.argv[1]]
		print "Exclicit message"
		try:
			w_map = getattr(w, 'map')
			print "Got map from worker %s: %s" % \
				(w, w_map())
		except AttributeError:
			pass
		except Exception as e:
			print "%s: %s" % (type(e), e)

		# workers_map[sys.argv[1]].run()


	for w in workers:
		ret = w.run(sys.argv[1:])
		if ret is None:
			continue

		print "Reply: %s" % ret.body
		if ret.final:
			break
