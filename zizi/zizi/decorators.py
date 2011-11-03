class ArgCountError(StandardError):
	pass

class VaArgs(object):
	pass

def accepts(*types):
	""" Function decorator. Checks that inputs given to decorated function
	are of the expected type.

	Parameters:
	types -- The expected types of the inputs to the decorated function.
			 Must specify type for each parameter.
	"""
	def info(fname, expected, actual, flag):
		""" Convenience function returns nicely formatted error/warning msg. """
		format = lambda types: ', '.join([str(t).split("'")[1] for t in types])
		expected, actual = format(expected), format(actual)
		msg = "'%s' method " % fname \
			  + ("accepts", "returns")[flag] + " (%s), but " % expected\
			  + ("was given", "result is")[flag] + " (%s)" % actual
		return msg

	try:
		def decorator(f):
			def newf(*args):
				for i in xrange(0, len(types)):
					# Check for vaargs argument
					if types[i] == VaArgs:
						return f(*args)
					try:
						arg = args[i]
					except IndexError:
						raise ArgCountError, "Invalid number of arguments: got %d expected %d" % \
							(len(args), len(types))

					if isinstance(types[i], type):
						if issubclass(type(arg), types[i]):
							continue
						else:
							try:
								types[i](arg)
								continue
							except ValueError:
								raise TypeError, info(f.__name__, types, tuple(map(type, args)), 0)

					elif callable(types[i]):
						if not types[i](arg):
							raise TypeError, info(f.__name__, types, tuple(map(type, args)), 0)

					else:
						raise TypeError, info(f.__name__, types, tuple(map(type, args)), 0)

				return f(*args)

			newf.__name__ = f.__name__
			return newf
		return decorator
	except TypeError, msg:
		raise TypeError, msg


