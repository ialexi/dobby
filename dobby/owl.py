# coding: utf-8
from thestral import Thestral
class Pig(Thestral):
	"""
	This is the simplest form of dispatcher. It is a reference implementation.
	It only responds to two commands: connect and disconnect.
	
	You can easily take a look at the code and see how it works. It is completely
	trivial. The more advanced dispathcher will be the queued dispatcher.
	"""
	def __init__(self, dolores):
		"""
		Listeners is the map of paths to listeners.
		"""
		self.dolores = dolores
		self.listeners = {}
		self.protocols = {}
	
	def update(self, sender, path, message):
		"""
		Has 3 special paths:
		::connect uid->path
		::disconnect uid->path
		::gone uid
		"""
		
		# First, some stuff applying to connect and disconnect
		if path == "::connect" or path == "::disconnect":
			# Get the id and path
			parts = message.split("->")
			if len(parts) != 2:
				# invalid.
				return
			
			# Extract separate arguments
			uid, cpath = parts
			
			# get the protocol referred to by the id
			protocol = self.dolores.getThestralById(uid)
			
			# Make sure that protocol exists
			if not protocol:
				return
			
		if path == "::connect":
			self.connect(uid, protocol, cpath)
		
		elif path == "::disconnect":
			self.disconnect(uid, protocol, cpath)
			
		elif path == "::gone":
			uid = message
			
			# make sure we don't do anything if there is nothing to do
			if not uid in self.protocols:
				return
			
			# Get protocol
			protocol = self.dolores.getThestralById(uid)
			
			# See if we got a protocol
			if not protocol:
				return
				
			# Get paths
			if not uid in self.protocols[uid]:
				return
			paths = self.protocols[uid]
						
			# remove protocol from listeners
			# TODO: clean up listener sets when empty.
			listeners = self.listeners
			for cpath in paths:
				listeners[cpath].remove(protocol)
		
		# We actually allow those special ones to go through, as well...
		if path in self.listeners:
			for l in self.listeners[path]:
				l.update(self, path, message)
				
	
	def connect(self, uid, protocol, path):
		# Add a listener set if necessary
		if not path in self.listeners:
			self.listeners[path] = set()
			
		# Add the protocol to the listener set
		self.listeners[path].add(protocol)
		
		# and add the listener to the protocol set
		if not uid in self.protocols: self.protocols[uid] = set()
		self.protocols[uid].add(path)
		
		# Send immediate notification to that protocol
		protocol.update(self, path, "")
	
	def disconnect(self, uid, protocol, path):
		# See if we need to do anything
		if not path in self.listeners:
			return

		# and again...
		if not protocol in self.listeners[path]:
			return

		# remove	
		self.listeners[path].remove(protocol)
		self.protocols[uid].remove(path)

		# And inform—but on a special disconnect channel because likely
		# our update is not wanted.
		protocol.update(self, "::+::disconnect", path)
