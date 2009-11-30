import sys
"""
Imperio is the text-based protocol for thestral.

There are three parts here: Imperio, the text-based handler which
processes or creates text commands, receiving them via receiveData
and sending them via any valid Thestral protocol commands.

To receive data, just supply a receiver object that implements the
Thestral protocol. It will "just work."

Imperio will wait for good and complete input-that is, a complete line.
So, whenever you have data to send imperio, just send it.
"""
class Imperio(object):
	"""
	The Imperio class translates between text serialization of Thestral and
	Python implemented Thestral objects. It implements Thestral, and as such,
	may receive Thestral commans, which it encodes and sends to its sender.
	
	It also may have a receiver, which is another Thestral implementer which
	will receive any parsed Thestral commands. To send unparsed data, call
	either receiveData or receiveLine.
	
	Set receiver to a thestral implementer (for instance, Dolores) to
	have it automatically receive updates from Imperio.
	
	Imperio, naturally, implements the protocol itself; however, to actually
	send data, it needs a sender, which can just be any object that implements
	a write(string) method.
	"""
	def __init__(self, receiver=None, sender=None, should_flush=False):
		self.receiver = receiver
		self.sender = sender
		self.should_flush = should_flush
		self.buffer = ""
	
	def update(self, sender, path, message):
		if self.sender:
			self.sender.write(path + "; " + message + "\n")
			if self.should_flush:
				self.sender.flush()
	
	def receiveData(self, data):
		"""
		Call with received data. It is your job to call this as a user of
		Imperio.
		"""
		self.buffer += data
		
	def checkBuffer(self):
		"""
		Checks the buffer to see if there is or are any line or lines in
		it. If there are, it will process them by calling receiveLine.
		"""
		if "\n" in self.buffer:
			lines = self.buffer.split("\n")
			last = lines[-1]
			lines = lines[:-1]
			self.buffer = last
			for l in lines:
				self.receiveLine(l)
		
	def receiveLine(self):
		"""
		Where all the good work goes on.
		
		Processes the line received, and dispatches an event to the receiver (if any).
		"""
		pieces = l.split(";")
		path = pieces[0]
		message = ""
		if len(pieces) > 1:
			message = pieces[1]
		
		# Now, send
		if self.receiver:
			self.receiver.update(self, path, message)

class Logger(Imperio):
	"""
	A simple subclass of Imperio which is sender-only, and which sends
	all of the data to a file (stdout by default)
	"""
	def __init__(self, f=sys.stdout):
		Imperio.__init__(self, sender=f, should_flush=True)

