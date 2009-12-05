from datetime import datetime
from time import mktime

try:
	import simplejson as json
except:
	import json

from thestral import Thestral
from twisted.internet.protocol import Protocol, Factory
from twisted.internet import reactor, task
from twisted.protocols.basic import LineReceiver
from twisted.web import server, resource

class TwistedDudleyResource(resource.Resource):
	isLeaf = True
	def __init__(self, dolores, receiver):
		self.dolores = dolores
		self.receiver = receiver
	
	def render_POST(self, request):
		try:
			request.content.seek(0, 0)
			content = request.content.read()
			commands = json.loads(content)
			for c in commands:
				if "message" in c and "path" in c:
					self.dolores.update(self, c["path"], c["message"])
			return "{success:true}"
		except:
			return "{error:true}"

class TwistedDudleyServer(object):
	def __init__(self, dolores, receiver=None, host="localhost", port=8004):
		self.dolores = dolores
		if not receiver: receiver = dolores
		self.receiver = receiver
		self.host = host
		self.port = port
		
		self.site = server.Site(TwistedDudleyResource(self.dolores, self.receiver))
		reactor.listenTCP(self.port, self.site)
		dolores.addStarter(reactor.run)