# coding: utf-8
from thestral import Thestral
import string
import random

# Dolores is a server implementation of the Thestral protocol.
class Dolores(Thestral):
	"""
	Dolores is a connection manager. That's pretty much it.
	
	Management of who is allowed to send what (like CONTROL priviledge) is handled through
	the caretaker, Filch (not implemented yet). Or some other delegate, if you'd prefer.
	"""
	def __init__(self, id="DOLORES-SERVER"):
		"""
		Initializes the Dolores server manager.
		"""
		self.id = id
		self.currentIndex = 0
		self.thestrals = {}
		self.starters = set()
		self.listeners = []
	
	def update(self, sender, path, message):
		"""
		sends an update to all listeners (not all registered thestrals)
		
		Sender is the original sender.
		"""
		for i in self.listeners:
			i.update(sender, path, message)
	
	def delegate(self, toWho):
		self.listeners.append(toWho)
	
	def start(self):
		"""
		Runs any methods associated with starting the server.
		
		Also, realize that starters is a set. This means that methods won't
		be called more than once, which allows, for instance, multiple Twisted
		clients to register reactor.run() or such.
		"""
		print "Instating Dolores High Inquisitor of Hogwarts"
		for s in self.starters:
			s()
	
	def registerThestral(self, thestral):
		"""
		Thestrals are dangerous beasts! They must be controlled and registered
		with Dolores! She'll give you back an id.
		"""
		thestral.id = self.getNextId()
		self.thestrals[thestral.id] = thestral
		return thestral.id
	
	def addStarter(self, starter):
		"""
		Adds a function to call on server start.
		"""
		self.starters.add(starter)
	
	def getNextId(self):
		"""
		Returns a new id.
		
		IDs are in the form:
		<dolores-id>-<random 32-character set of letters and digits>-<incrementing number>
		"""
		choose_from = string.ascii_letters + string.digits
		id = self.id + "-"
		for i in range(0, 32):
			id += random.choice(choose_from)
		self.currentIndex += 1
		id += "-" + str(self.currentIndex)
		return id
	
	def getThestralById(self, id):
		"""
		Returns a Thestral instance identified by its id.
		"""
		if id in self.thestrals:
			return self.thestrals[id]
		return None
	
	def unregisterThestral(self, thestral):
		"""
		Unregisters a Thestral and sends the ::gone signal so anyone connecting
		that thestral can know about it.
		"""
		if thestral.id in self.thestrals:
			del self.thestrals[thestral.id]
			self.update(self, "::gone", thestral.id)
		