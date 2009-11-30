import urllib, urllib2
HOST = "localhost"
PORT = 8003

class CorneliusError: pass

def update(path, message):
	global HOST, PORT
	result = urllib2.urlopen("http://" + HOST + ":" + str(PORT) + "/" + urllib.quote(path + ";" + message))
	res = result.read()
	if res == "{sent:true}":
		return True
	else:
		raise CorneliusError()

def connect(uid, toWhat):
	return update("::connect", uid + "->" + toWhat)

def disconnect(uid, fromWhat):
	return update("::disconnect", uid + "->" + fromWhat)
