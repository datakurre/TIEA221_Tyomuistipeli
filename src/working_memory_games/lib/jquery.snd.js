/** This is a very qute sound preloading and jquery integration for
 *  playing with jquery's fx queue.
 * 
 * Basically you use it like this:
 *
 *  $.preload('hello', '/hello.[mp3,ogg]');
 *  $.preload('bye', '/snd/bye.[mp3,ogg]');
 *  $('body').one('preloaded', function(){
 *    $('body').play('hello').play('hello').play('bye');
 *  });
 *
 * Copyright 2013, Matti Katila
 */
(function() {

var parentWindow;

window.addEventListener("message", function(event) {
    if (event !== undefined && event.data !== undefined) {
        if (event.data === "CONNECT") {
            console.log("CONNECTED");
            parentWindow = event.source;
        } else if (/^PRELOAD:.*/.test(event.data)) {
            console.log(event.data);
        } else if (/^PLAY:.*/.test(event.data)) {
            console.log(event.data);
        }
    }
}, false);

jQuery(function($) {

    $._preload = {
        iOS: (navigator.userAgent.match(/(iPad|iPhone|iPod)/g) ? true : false),
        audio: document.createElement('audio'),
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
            return this.queue('fx', function() {
                if (parentWindow !== undefined
                        && parentWindow.postMessage !== undefined) {
                    parentWindow.postMessage('PLAY:' + id, '*');
                    return;
                }

                var elem = this;
                var audio = $._preload.loaded[id];

                // listen complete signal
                $($._preload.audio).unbind('ended');
                $($._preload.audio).bind('ended', function(event) {
                    var currentTime = $._preload.audio.currentTime,
                        duration = $._preload.audio.duration;

                    // keep going on fake endings :)
                    if (currentTime < duration) {
                        $._preload.audio.play();
                        return;
                    }

                    // completion frees the queue
                    jQuery.dequeue(elem, "fx");
                });
                if (audio !== undefined) {
                    //console.log('Start play');
                    //console.log(audio);
                    $._preload.audio.src = audio;
                    $._preload.audio.play();
                }
            });
        }
    });
    $.extend({
        preload: function(id, uri) {
            console.log("PRELOAD");
            if (parentWindow !== undefined
                    && parentWindow.postMessage !== undefined) {
                parentWindow.postMessage('PRELOAD:' + id + ':' + uri, '*');
                return;
            }

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
                urls = [url];
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
                    $.ajax({
                        type: 'get',
                        url: url,
                        complete: function(data) {
                            console.log($._preload.processing);
                            delete $._preload.processing[id];

                            //var audio = $('<audio src="'+url+'"></audio>');
                            $._preload.loaded[id] = url; //audio;

                            if (jQuery.isEmptyObject($._preload.processing)) {
                                if ($._preload.iOS) {
                                    $('body').append('<div id="iOShit" style="position:absolute;top:0%;z-index:500;left:0%;width:100%;height:100%" ></div>');
                                    $('#iOShit')[0].ontouchstart = function(event) {
                                        $('#iOShit').remove();
                                        $('body').trigger('preloaded');
                                    };
                                } else
                                    $('body').trigger('preloaded');
                            }

                            // XXX todo, should we also wait for canplaythrough?
                            $($._preload.audio).bind('canplaythrough', function(event){
                                //console.log(event);
                            });
                        }
                    });
                }
                initAudio(urls[i]);
                break;
            }
        }
    });

});

}).call(this);
