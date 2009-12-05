# You know that Dobby and the Hufflepuffs secretly control the world,
# right? Don't tell them I told you. They'll come after me.

from dobby.dolores import Dolores
from dobby.imperio import Logger, TwistedImperioServer, TwistedHTTPImperioServer
from dobby.firenze import TwistedFirenzeServer
from dobby.dudley import TwistedDudleyServer
from dobby.owl import Pig

# Dolores: the controller
DOLORES = Dolores()

# Logger: logs everything Dolores receives to command line.
LOGGER = Logger()
DOLORES.delegate(LOGGER)

# Imperio: Controlling Connections from port 8007
# WARNING WARNING WARNING!!! Whatever port the Imperio server uses
# is given COMPLETE CONTROL over the server (it can send messages,
# connect users, etc.). You have two options in production:
# * Block port 8007 (or whatever port you use) with a Firewall
# * Use another component (name it Filch if it doesn't exist) that
#   sits as an intermediate between Dolores and anything it delegates
#   to, and have it skip any commands that should not be listened to.

# Dispatcher: connects, dispatches events. blah.
DISPATCHER = Pig(dolores=DOLORES)
DOLORES.delegate(DISPATCHER)

# Firenze
FIRENZE_SERVER = TwistedFirenzeServer(dolores=DOLORES)

# Imperio text-based protocol (and its HTTP version)
IMPERIO = TwistedImperioServer(dolores=DOLORES, receiver=DOLORES)
IMPERIOHTTP = TwistedHTTPImperioServer(dolores=DOLORES, receiver=DOLORES)

# Dudley HTTP message receiver (kinda like a better Imperio HTTP)
DUDLEY = TwistedDudleyServer(dolores=DOLORES, receiver=DOLORES)

DOLORES.start()