# You know that Dobby and the Hufflepuffs secretly control the world,
# right? Don't tell them I told you. They'll come after me.

from dobby.dolores import Dolores
from dobby.imperio import Logger
from dobby.firenze import TwistedFirenzeServer
from dobby.owl import Pig

# Dolores: the controller
DOLORES = Dolores()

# Logger: logs everything Dolores receives to command line.
#LOGGER = Logger()
#DOLORES.delgate(LOGGER)

# Dispatcher: connects, dispatches events. blah.
DISPATCHER = Pig(dolores=DOLORES)
DOLORES.delegate(DISPATCHER)

# 
FIRENZE_SERVER = TwistedFirenzeServer(dolores=DOLORES)
#IMPERIO = imperio.TwistedImperio(dolores=DOLORES, receiver=DOLORES)


DOLORES.start()