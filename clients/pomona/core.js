// ==========================================================================
// Project:   Pomona
// Copyright: ©2009 TPSi and Alex Iskander.
// ==========================================================================
/*globals Pomona */

/** @namespace

	@extends SC.Object
*/
Pomona = SC.Object.create(
	/** @scope Pomona.prototype */ {
	
	NAMESPACE: 'Pomona',
	VERSION: '0.1.0',
	Firenze: SC.Object.extend({
		host: document.domain,
		prefix: "comet/",
		port: 4020,
		protocol: "http",
		crossPort: YES,
		debug: YES,
		reconnectWith: "",
		
		init: function() {
			if (this.crossPort) document.domain = document.domain;
			
			// begin the comet loop
			this._beginNextRequest();
		},
		
		_beginNextRequest: function() {
			this.timer = undefined;
			var pre = "";
			if (this.host.length !== 0) pre = this.protocol + "://" + this.host + ":" + this.port;
			var url = pre + "/" + this.prefix + this.reconnectWith;
			if (this.get("debug")) {
				console.debug("Firenze Request: " + url);
			}
			SC.Request.getUrl(url)
				.json().notify(this, "_receive").send();
		},
		
		_receive: function(response) {
			var body = response.get("body");
			if (body) {
				this.reconnectWith = body.reconnectWith;

				var updates = body.updates; // should at least exist.
				if (updates) {
					var i = 0, len = updates.length;
					for (i = 0; i < len; i++) {
						this.update(updates[i].path, updates[i].message);
					}
					this._beginNextRequest();
					
					// all is well
					return;
				}
			}
			
			// not okay, so we wait for a sec, then try again
			if (this.timer) this.timer.invalidate();
			this.timer = SC.Timer.schedule({
				interval: 1000,
				target: this,
				action: "_beginNextRequest"
			});
		},
		
		update: function(path, listener) {
			console.error(path + " " + listener);
		}
	})
}) ;
