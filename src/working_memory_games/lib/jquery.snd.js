
/** This is a very qute sound preloading and jquery integration for 
 *  playing with jquery's fx queue.
 * 
 * Basically you use it like this:
 *
 *  $.preload('hello', '/hello.[mp3,ogg]');
 *  $.preload('bye', '/snd/bye.[mp3,ogg]');
 *  $('body').on('preloaded', function(){
 *    $('body').play('hello').play('hello').play('bye');
 *  });
 *
 * Copyright 2013, Matti Katila
 */

(function($) {
    $._preload = {
	loaded: {},
	processing: {}
    };
    $.fn.extend({
        snd: function(id) {
            var audio = $._preload.loaded[id];
            return audio;
        },
        play: function(id) {
	    if (id === undefined) {
		console.trace();
		return;
	    }

	    return this.queue("fx", function() {
		var elem = this;
		var audio = $._preload.loaded[id];

		// listen complete signal
		$(audio).bind('ended', function(event){

		    // keep going on fake endings :)
		    if (audio[0].currentTime < audio[0].duration) {
			audio[0].plsuditay();
			return;
		    }
		    // completion frees the queue
		    jQuery.dequeue( elem, "fx" );
		});
		if (audio !== undefined) {
		    console.log('Start play');
		    console.log(audio);
		    audio[0].play();
		}
	    });
        }
    });
    $.extend({
        preload: function(id, uri) {
	    $._preload.processing[id] = true;
	    var a = uri.indexOf('['),
	        b = uri.indexOf(','),
	        c = uri.indexOf(']'),
  	        urls = [];
	    if (0 < a && a < b && b < c) {
		var pre = uri.split('[', 2);
		var post = pre[1].split(']', 2);
		var list = post[0].split(',');
		for (var i=0; i<list.length; i++) {
		    urls.push(pre[0]+list[i]+post[1]);
		}
	    } else {
		urls = [ url ];
	    }

	    var dumb = document.createElement('audio');
	    for (var i=0; i<urls.length; i++) {
		if (urls[i].search(/mp3/i) > 0
		    && !(dumb.canPlayType && dumb.canPlayType('audio/mpeg;').replace(/no/, '')))
		    continue;
		if (urls[i].search(/ogg/i) > 0
		    && !(dumb.canPlayType && dumb.canPlayType('audio/ogg; codecs="vorbis"').replace(/no/, '')))
		    continue;

		function initAudio(url) {
		
		    $.get(url).complete(function(data){
			console.log($._preload.processing);
			delete $._preload.processing[id];
			
			var audio = $('<audio src="'+url+'"></audio>');
			$._preload.loaded[id] = audio;

			if (jQuery.isEmptyObject($._preload.processing))
			    $('body').trigger('preloaded');

			// XXX todo, should we also wait for canplaythrough?
			$(audio).bind('canplaythrough', function(event){
			    //console.log(event);
			});
		    });
		}
		initAudio(urls[i]);
		break;
	    }
        }
    })
})(jQuery);
