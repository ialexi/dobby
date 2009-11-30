import sys
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, task
from twisted.protocols.basic import LineReceiver
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import urllib

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
		
	def receiveLine(self, l):
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


class TwistedImperioConnection(LineReceiver):
	def connectionMade(self):
		self.imperio = Imperio(self.factory.receiver, self)

	def lineReceived(self, line):
		# Send to so and so...
		if line == "::exit":
			self.transport.loseConnection()
			return
		self.imperio.receiveLine(line)
	
	def write(self, what):
		self.transport.write(what)

class TwistedImperioServer(Factory):
	def __init__(self, dolores, receiver=None, host="localhost", port=8007):
		self.dolores = dolores
		if not receiver: receiver = dolores
		self.receiver = receiver
		self.host = host
		self.port = port
		self.protocol = TwistedImperioConnection
		reactor.listenTCP(self.port, self)
		dolores.addStarter(reactor.run)


class TwistedHTTPImperioConnection(LineReceiver):
	def connectionMade(self):
		self.imperio = Imperio(self.factory.receiver, self)

	def lineReceived(self, line):
		# We pretend to support HTTP GET (even though logically, PUT or POST would be better)
		# Still, it is all in the URL for simplicity
		if line.startswith("GET"):
			self.receivedGET = True
			l = line.split(" ")
			if len(l) != 3:
				self.transport.loseConnection()
				return
		
			command = urllib.unquote(l[1][1:])
		
			# Are we a somebody?
			self.imperio.receiveLine(command)
			
			now = datetime.now()
			stamp = mktime(now.timetuple())
			data = "{sent:true}"
			headers = "HTTP/1.1 200 OK\r\n"
			headers += "Date: " + format_date_time(stamp) + "\r\n"
			headers += "Server: Firenze instance, probably on Dolores.\r\n"
			headers += "Content-Length: " + str(len(data)) + "\r\n"
			headers += "Content-Type: application/json\r\n\r\n"
			self.transport.write(headers)
			self.transport.write(data)
			self.transport.loseConnection()

	def write(self, what):
		self.transport.write(what)

class TwistedHTTPImperioServer(Factory):
	def __init__(self, dolores, receiver=None, host="localhost", port=8003):
		self.dolores = dolores
		if not receiver: receiver = dolores
		self.receiver = receiver
		self.host = host
		self.port = port
		self.protocol = TwistedHTTPImperioConnection
		reactor.listenTCP(self.port, self)
		dolores.addStarter(reactor.run)

