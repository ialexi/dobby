# coding: utf-8
"""
The Thestral protocol is really a single command: a message-passing one.
Also, each Thestral must have an id (well, in most cases). But that will
likely be handled for you.

That is all. Everything else can be expressed as said message. It really makes
things simpler when you think that way.

Cue: Boring backstory.

See, we _used_ to have a bunch of commands, some for server, some for this, some
for that... but that meant special parsers for each, when all that is really needed
is a path and some data.

Also, this means that commands can be relayed through several Thestrals—even across
servers.

All Thestrals must have identifiers. They should only be the same identifier when they
are mirrors (or, to use the quantum-mechanical-sounding term, entangled) with another
Thestral.

Identifiers are usually managed by Dolores, the id manager. 
"""
class Thestral:
	def __init__(self):
		self.id = "--no--id--"
	
	def update(self, source, path, data):
		"""
		source: who ordered the update (a thestral object or None)
		
		path: The path that was updated.
		
		data: data to go along with that.
		"""
		pass




