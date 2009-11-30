# coding: utf-8
"""
Firenze is a server that allows long-polling. It serves its updates
in JSON format for really easy parsing on the client.

Since Firenze is always initiated by the client, client implementations
(such as TwistedFirenze) tell Dolores about connection objects.

Rather simple: Firenze implements no queuing at a manager level. Instead, each individual
connection keeps a queue of messages to send for up to RECONNECT_TIMEOUT seconds. This
is not usually a problem because client-side Firenzes should usually reconnect right away.
However, it could cause problems if the connection between the server and all clients was
interrupted and there are thousands of clients each receiving hundreds of messages a second.
It is likely such large-scale deployments would run into other issues first—for instance,
hard limits on the number of connections which can be handled by the machine. Besides,
it is not really a good idea to send hundreds of messages in a second to individual clients,
anyway—much better to send fewer, more important messages.

Firenzes are synchronous. They will send whatever they have roughly whenever they get it available,
but only when the client requests it. The client requests with its previous UID (this expires,
of course, after only 30 seconds or so). There is a map between UIDs and Firenze instances,
and when new clients are attached with a previous UID, the connection is supplied to that Firenze;
the map, however, is adjusted merely by adding the new UID—not deleting the old. The Firenze instance
knows its old and new ids; if it gets the new one, it can clear its queue up to the point it sent
last, and start afresh with the rest. If it gets the old one, it just sends the entire queue.

Each Firenze instance has a timer. It expires after the manager's MAX_CONNECTION_LENGTH
—30 seconds, by default. At this time, it will send whatever it has (nothing). However,
if it receives a message, this timer will be replaced with one that expires after the
DELAY_TRANSMISSION property—.5 seconds, by default. This allows bundling of messages.

If messages will never be bundled—or, if you want to send messages immediately, damn
the consequences—you might as well set this to zero.

Firenzes have implementations separate from the main Firenze controlling stuff. The only
current implementation is the Twisted implementation. It is up to the implementation to
implement the timer, but it only needs to implement changeTimeout to do so.

The basic structure of the Twisted implementation is as such:
* Firenze
* FirenzeManager
* TwistedFirenzeManager, a Firenze manager that creates TwistedFirenzes.
* TwistedFirenzeFactory, a Twisted Factory object.
* TwistedFirenzeConnection, a Twisted protocol.
* TwistedFirenze, an implementation of a Firenze (a Thestral) that is constructed
  with an instance of TwistedFirenzeConnection. Calls timer methods on reactor to set up callbacks, etc.
"""
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
import urlparse
from thestral import Thestral
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, task
from twisted.protocols.basic import LineReceiver

try:
	import simplejson
except:
	import json

class Firenze(Thestral):
	"""
	Firenzes that have pending messages are connected to each other in a linked list.
	
	"""
	def __init__(self, manager):
		self.manager = manager
		self.pendingTransmission = None
		self.queue = []
		self.isReadyToSend = False
		self.isWaitingToSend = False
		self.iteration = 0
		self.hasSentAnything = False
	
	def update(self, source, path, message):
		"""
		Well, you can leave this as-is... or you can do something a bit more clever.
		For instance, if you are integrating with 
		"""
		self.addToQueue(source, path, message)
	
	def readyToSend(self):
		"""
		This should be called by subclasses when they are able to send data.
		It will set isReadyToSend, or will send whatever is already ready to send.
		"""
		self.isReadyToSend = True
		if self.isWaitingToSend or not self.hasSentAnything:
			self.isWaitingToSend = False
			self.processQueue()
		else:
			self.setTimeout(self.manager.MAX_CONNECTION_LENGTH)
	
	def addToQueue(self, source, path, message):
		"""
		Adds an item to the queue, then sets the timeout to DELAY_TRANSMISSION—if
		transmission is not already pending.
		
		Separated out so that its caller, update, may be overriden
		to run from a specific thread.
		"""
		self.queue.append({"path": path, "message": message})
		self.isWaitingToSend = True
		
		# If we are all set, go ahead and try to process
		if not self.pendingTransmission and self.readyToSend:
			self.setTimeout(self.manager.DELAY_TRANSMISSION)
			self.pendingTransmission = True
	
	def processQueue(self):
		"""
		Processes the queue and calls send() with the resulting data.
		"""
		# No longer pending
		self.pendingTransmission = False
		
		if not self.isReadyToSend:
			return
		
		# Generate data
		data = json.dumps({
			"updates": self.queue,
			"reconnectWith": self.id + "/" + str(len(self.queue))
		}) + "\r\n\r\n"
		
		now = datetime.now()
		stamp = mktime(now.timetuple())
		
		headers = "HTTP/1.1 200 OK\r\n"
		headers += "Date: " + format_date_time(stamp) + "\r\n"
		headers += "Server: Firenze instance, probably on Dolores.\r\n"
		headers += "Content-Length: " + str(len(data)) + "\r\n"
		headers += "Content-Type: application/json\r\n\r\n"
		
		self.send(headers, data)
		self.isReadyToSend = False
		self.isWaitingToSend = False
		self.hasSentAnything = True
		
		self.setCancelTimeout(self.manager.TIMEOUT_LENGTH)
	
	def cancel(self):
		self.manager.stop(self)
	
	def confirm(self, count):
		"""
		Confirms that the first X items in the queue were sent—removing them
		from the queue.
		
		Safe, because we are completely synchronous. So there.
		"""
		del self.queue[0:count]
		if len(self.queue) > 0:
			self.isWaitingToSend = True
		else:
			self.isWaitingToSend = False
	
	def send(self, headers, data):
		pass # Implementors need to implement this.
	
	def setTimeout(self, delay):
		pass # Implementors: Implement this.
	
	def setCancelTimeout(self, delay):
		pass

class FirenzeManager(object):
	def __init__(self, dolores, MAX_CONNECTION_LENGTH=30, DELAY_TRANSMISSION=.25, TIMEOUT_LENGTH=30):
		self.dolores = dolores
		self.MAX_CONNECTION_LENGTH = MAX_CONNECTION_LENGTH
		self.DELAY_TRANSMISSION = DELAY_TRANSMISSION
		self.TIMEOUT_LENGTH = TIMEOUT_LENGTH
	def beginNewSession(self, connection):
		firenze = TwistedFirenze(self)
		firenzeId = self.dolores.registerThestral(firenze)
		firenze.supplyConnection(connection)

	def resumeSession(self, rw, connection):
		# The reconnectWith holds: uid/confirmCount
		# Split by slash
		pieces = rw.split("/")
		
		# get uid
		uid = pieces[0]
		
		# confirm is by default 0, but read if possible
		confirm = 0
		if len(pieces) > 1:
			confirm = int(pieces[1])
		
		firenze = self.dolores.getThestralById(uid)
		if not firenze:
			self.beginNewSession(connection)
			return
		
		firenze.confirm(confirm)
		firenze.supplyConnection(connection)
	def stop(self, what):
		self.dolores.unregisterThestral(what)
		
	

class TwistedFirenze(Firenze):
	def __init__(self, manager):
		Firenze.__init__(self, manager)
		self._currentTimeout = None
		self._currentCancelTimeout = None
		self.dolores = self.manager.dolores
	
	def supplyConnection(self, connection):
		self.connection = connection
		self.readyToSend()
	
	def send(self, headers, data):
		self.twistedSend(headers, data)
	
	def twistedSend(self, headers, data):
		self.connection.transport.write(headers)
		self.connection.transport.write(data)
		self.connection.transport.loseConnection()
		self.connection = None
		
	def setTimeout(self, duration): # This should already be running in the right thread, I think.
		if self._currentTimeout:
			self._currentTimeout.cancel()
			self._currentTimeout = None
		if duration == 0:
			self.processQueue()
			return
		self._currentTimeout = reactor.callLater(duration, self._handleTimeout)
		
	def setCancelTimeout(self, duration): # This should already be running in the right thread, I think.
		if self._currentCancelTimeout:
			self._currentCancelTimeout.cancel()
			self._currentCancelTimeout = None
		if duration == 0:
			self.cancel()
			return
		self._currentCancelTimeout = reactor.callLater(duration, self._handleCancelTimeout)
	
	def _handleCancelTimeout(self):
		self._currentTimeout = None
		self.cancel()
	
	def _handleTimeout(self):
		self._currentTimeout = None
		self.processQueue()

class TwistedFirenzeConnection(LineReceiver):
	def connectionMade(self):
		self.receivedGET = False
		self.dolores = self.factory.dolores
		self.manager = self.factory.manager
	
	def lineReceived(self, line):
		# We ignore all headers. Just get on the phone!
		if line.startswith("GET"):
			self.receivedGET = True
			l = line.split(" ")
			if len(l) != 3:
				self.transport.loseConnection()
				return
			
			uid = l[1]
			
			# Are we a somebody?
			if uid.strip() == "":
				self.manager.beginNewSession(self)
			else:
				self.manager.resumeSession(uid[1:], self)

class TwistedFirenzeServer(Factory):
	def __init__(self, dolores, host="localhost", port=8008):
		self.manager = FirenzeManager(dolores)
		self.dolores = dolores
		self.host = host
		self.port = port
		self.protocol = TwistedFirenzeConnection
		reactor.listenTCP(self.port, self)
		dolores.addStarter(reactor.run)


