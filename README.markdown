Dobby is a lightweight push server.
Its core is Thestral, a simple protocol-independent interface for pushing
information around.

Quick+Simple Part
-----------------
At its most simple, Dobby is a lightweight but flexible event-based system
which includes a Comet server component. **This all works.**

Thoughts
---------
Dobby can, however, be much more—a secret architect behind the scenes.

**Except that none of this is possible yet. It is just in planning.**

Think of how we actually work: do we ever actively "get" information?

No. Our brains push an instruction to our fingers, eyes, or whatever;
our eyes, fingers, or whatever push information back to us. Each component
is completely independent from the others.

So, why do we expect our web apps to send an HTTP GET request and receive
as part of that request? Would it not make more sense to simply tell the
server, "Hey, I'm interested in this information," and have the server
automatically send us not only all the pertinent information, but keep
updating it as more becomes available? (Long running queries can respond
immediately—even queries that cross servers don't pose any problems).

For performance reasons, any immediately-retrievable data should be sent
in that same request that "subscribed" the client; however, the data sent
is in the push format.

The first and most important thing is that you only *ever* have one
"receive" processor on the client side. You never use SC.Request; you
instead use firenzee.attach("/my/objects")

After that, the options vary: you might have a typical server-side setup,
or your server might even be written with some framework sitting on top
of Dobby (in which, instead of requesting URLs, the client sends messages
through Dobby, and the server receives and sends messages back).

This latter arrangement would benefit greatly from some sort of web sockets
implementation that would be higher performance than transferring everything
through individual HTTP requests.