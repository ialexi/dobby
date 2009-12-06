Dobby is a lightweight push server.
Its core is Thestral, a simple protocol-independent interface for pushing
information around.

Quick+Simple Part
-----------------
At its most simple, Dobby is a lightweight but flexible event-based system
which includes a Comet server component.

Warning
-------
**First, this walkthrough really isn't thorough enough.**
Now, the other issues:
a) Dobby is under somewhat heavy development.
b) You should not use in production without understanding a _little_
   of the innards—which is not difficult to do, given that it is _extremely_
   simple. There are some security issues, such as ports that would likely need
   blocking.

Conclusion: Use Dobby if you a) just want something quick and not necessarily
permanent, or b) want to actually learn Dobby's code somewhat fully and 
help out. :)

How you use
-----------
Typically, an application using Dobby will have three parts:
* Dobby
* Back-end (Django, Rails, etc.)
* Front-end (SproutCore)

The Workflow
------------
In short:

* Pomona (SproutCore framework for Dobby) connects to Dobby.
* Dobby sends Pomona an ID.
* Pomona calls two URLs given two it to connect or disconnect from
  paths/channels.
	* URLs are implemented in back-end (Django, etc).
	* The ID is sent with these requests.
* Back-end tells Dobby to connect the client to the path.
	* Back-end can do any authorization it wants here, however it wants.
	  If it doesn't want to allow the connection, it can just not tell Dobby.
* Back-end sends updates to Dobby, whenever it pleases.


Pomona is quite nice in that it keeps track of connections for you, so will
automatically reconnect to anything should the connection be dropped.

How to Implement-Client Side
----------------------------
The client side should be implemented using Pomona, the SproutCore
framework for Dobby.

**TODO:** Write here how to clone Pomona and set it up as a framework.
You may very well already know how to do that anyway...

Typically, you set up the Dobby connection in whatever Data Source you use.
It is really very simple. For example, you may have the following init function:

		init: function(){
			// by default, tries to go through "/comet/", so you need
			// to proxy using sc-server during development.
			this.firenze = Pomona.Firenze.create({
				connectUrl: "/server/connect/%@",  // the paths to use to connect+disconnect
				disconnectUrl: "/server/disconnect/%@"
			});
			
			// connect paths to functions
			this.firenze.connect("contacts", this, "contactReceived");
		},
		
		contactReceived: function(path, message) {
			if (message.trim() === "") return; // first message sent—to confirm connection—is blank.
			
			// read the data
			var data = JSON.parse(message);
			
			// loada the record
			Contacts.store.loadRecords(Contacts.Group, [data]);
		}

Can't get much simpler than that!

How to Implement: Back-end with Django
--------------------------------------
First, you need to add the "cornelius" package to your Django project.
		git clone git://github.com/ialexi/cornelius.git

Now, you have to enable connection and disconnection. Some lines like this in urls.py should do it:
		(r'^contacts/connect/(?P&lt;uid&gt;[^\s]+)$', "contacts.views.connect"),
		(r'^contacts/disconnect/(?P&lt;uid&gt;[^\s]+)$', "contacts.views.connect")

In your views (contacts/views.py in the above example), you would add some views.
**Note that, while the following works, I need to update it to use cornelius.dudley, which**
**is vastly superior, oddly enough, to "imperio."**
		# These don't do ANY authentication. You can just check the paths received.
		# The paths are an array of strings, as you can see.
		def connect(request, uid):
			paths = json.loads(request.raw_post_data)
			# Unfortunately, this will send out a request for each. Optimizations would be nice...
			for p in paths:
				cornelius.imperio.connect(uid, p)
			return HttpResponse("{sent:true}", mimetype="application/json")

		def disconnect(request, uid):
			paths = json.loads(request.raw_post_data)
			for p in paths:
				cornelius.imperio.disconnect(uid, p)
			return HttpResponse("{sent:true}", mimetype="application/json")


You will, of course, also need to include json and cornelius:
		import cornelius.imperio
		try:
			import simplejson as json # For <= 2.5
		except ImportError: # for 2.6+
			import json


And now, you need to actually send messages. The easiest way is to add some post-save hooks.
I add mine in models.py:
		# Comet alerters
		def contact_saved(sender, **kwargs):
			try:
				instance = kwargs["instance"]
				cornelius.imperio.update("contacts", json.dumps(instance.toRaw()))
			except:
				pass

		post_save.connect(contact_saved, sender=Contact)


And that's it.