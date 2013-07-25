/** This is a very cute sound preloading and jquery integration for
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
 * Copyright 2013, Matti Katila, Asko Soukka
 */
(function() {

var isMaster = (
    window.parent === window
    || window.parent === null
    || window.parent === undefined
);

window.addEventListener('message', function(event) {
    var parts;
    if (event !== undefined && event.data !== undefined) {
        if (/^PRELOAD:[^:]+:.+/.test(event.data)) {
            console.log("PARENT", event.data);
            parts = /^PRELOAD:([^:]+):(.+)/.exec(event.data);
            $.preload(parts[1], parts[2], function() {
               event.source.postMessage('PRELOADED', '*');
            });
        } else if (/^PRELOADED$/.test(event.data)) {
            console.log("CHILD", event.data);
            $('body').trigger('preloaded');

        } else if (/^PLAY:.+/.test(event.data)) {
            console.log("PARENT", event.data);
            parts = /^PLAY:(.+)/.exec(event.data);
            $($._preload.audio).play(parts[1], function() {
                $($._preload.audio).dequeue('fx');
                event.source.postMessage('DEQUEUE', '*');
            });
        } else if (/^DEQUEUE$/.test(event.data)) {
            console.log("CHILD", event.data);
            if ($._preload.queued.length > 0) {
                $._preload.queued.shift().dequeue('fx');
            }
        }
    }
}, false);

jQuery(function($) {

    $._preload = {
        iOS: (navigator.userAgent.match(/(iPad|iPhone|iPod)/g) ? true : false),
        audio: document.createElement('audio'),
        formats: {},
        loaded: {},
        processing: {},
        queued: []
    };

    // Populate supported audio types:
    if (typeof $._preload.audio.canPlayType === 'function') {
        if ($._preload.audio.canPlayType('audio/mpeg;')
                            .replace(/no/, '')) {
            $._preload.formats['mp3'] = true;
        }
        if ($._preload.audio.canPlayType('audio/ogg; codecs="vorbis"')
                            .replace(/no/, '')) {
            $._preload.formats['ogg'] = true;
        }
    } else {
        $._preload.formats['mp3'] = true;
    }

    // Fix broken audio tag with a mock
    if (!(typeof $._preload.audio.play === 'function')) {
        $._preload.audio.play = function() { $(this).trigger('ended'); };
    }

    $.extend({
        preload: function(id, uri, callback) {
            if (isMaster === false) {
                parent.window.postMessage('PRELOAD:' + id + ':' + uri, '*');
                return;
            }
            console.log("PRELOADING:", id, uri);

            $._preload.processing[id] = true;

            var a = uri.indexOf('['),
                b = uri.indexOf(','),
                c = uri.indexOf(']'),
                urls = [], i;
            if (0 < a && a < b && b < c) {
                var pre = uri.split('[', 2);
                var post = pre[1].split(']', 2);
                var list = post[0].split(',');
                for (i = 0; i < list.length; i++) {
                    urls.push(pre[0] + list[i] + post[1]);
                }
            } else {
                urls = [uri];
            }

            var initAudio = function(url) { return $.ajax({
                type: 'get',
                url: url,
                complete: function() {
                    console.log("COMPLETE:", id, url);

                    delete $._preload.processing[id];
                    $._preload.loaded[id] = url;

                    if (jQuery.isEmptyObject($._preload.processing)) {
                        if ($._preload.iOS === true) {
                            if (isMaster === false) alert("WTF?");
                            console.log("IOS AUDIO DETECTED");
                            $('<div></div>').css({
                                'position': 'absolute',
                                'top': '0', 'right': '0',
                                'bottom': '0', 'left': '0',
                                'z-index': '99999'
                            }).bind('touchstart', function() {
                                console.log("IOS AUDIO ACTIVATED");
                                $(this).remove();
                                $._preload.iOS = false;
                                $._preload.audio.load();
                                if (typeof callback === 'function') {
                                    callback();
                                } else {
                                    $('body').trigger('preloaded');
                                }
                            }).appendTo($('body'));
                        } else {
                            if (typeof callback === 'function') {
                                callback();
                            } else {
                                $('body').trigger('preloaded');
                            }
                        }
                    }
                    // TODO: should we also wait for canplaythrough?
                    // $($._preload.audio).bind('canplaythrough', function(){
                    // });
                }});
            };

            for (i = 0; i < urls.length; i++) {
                if (urls[i].search(/mp3/i) > 0 && $._preload.formats['mp3']) {
                    initAudio(urls[i]);
                    break;
                }
                if (urls[i].search(/ogg/i) > 0 && $._preload.formats['ogg']) {
                    initAudio(urls[i]);
                    break;
                }
            }
        }
    });

    $.fn.extend({
        snd: function(id) {
            return $._preload.loaded[id];
        },
        play: function(id, callback) {
            var that = this;
            if (id !== null && id !== undefined && isMaster === true) {
                return this.queue('fx', function() {
                    var audio = $._preload.loaded[id];

                    // Listen complete signal:
                    $($._preload.audio).unbind('ended')
                                       .bind('ended', function() {
                        var currentTime = $._preload.audio.currentTime,
                            duration = $._preload.audio.duration;

                        // Keep going on fake endings :)
                        if (currentTime < duration) {
                            $._preload.audio.play();

                        // Completion frees the queue:
                        } if (typeof callback === 'function') {
                            callback();
                        } else {
                            that.dequeue('fx');
                        }
                    });

                    // Play:
                    if (audio !== null && audio !== undefined) {
                        $._preload.audio.src = audio;
                        $._preload.audio.play();
                    }
                });
            } else if (id !== null && id !== undefined) {
                return this.queue('fx', function() {
                    $._preload.queued.push(that);
                    window.parent.postMessage('PLAY:' + id, '*');
                });
            } else {
                console.trace();
                return this;
            }
        }
    });
});

}).call(this);
