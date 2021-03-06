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

// If the current frame is not master, $.preload and $.play calls
// are send to window.parent via postMessaging.
var isMaster = (
    window.parent === window
    || window.parent === null
    || typeof window.parent === "undefined"
);

// Web Audio API is enabled only on iOS, where it's currently tested to work:
var createAudioContext = function() {
    if (!navigator.userAgent.match(/(iPad|iPhone|iPod)/g)) {
        return false;
    }
    if (typeof window.AudioContext !== "undefined") {
        return new window.AudioContext();
    }
    if (typeof window.webkitAudioContext !== "undefined") {
        return new window.webkitAudioContext();
    }
    return false;
};

// Handle postMessaging between the main page and iframe:
(window.addEventListener || function() {})('message', function(event) {
    var parts, id;
    if (event !== undefined && event.data !== undefined) {
        if (/^PRELOAD:[^:]+:.+/.test(event.data)) {
            console.log("PARENT", event.data);
            parts = /^PRELOAD:([^:]+):(.+)/.exec(event.data);
            $.preload(parts[1], parts[2], function() {
               event.source.postMessage('PRELOADED', ['*']);
            });
        } else if (/^PRELOADED$/.test(event.data)) {
            console.log("CHILD", event.data);
            $('body').trigger('preloaded');

        } else if (/^PLAY:.+/.test(event.data)) {
            console.log("PARENT", event.data);
            parts = /^PLAY:(.+)/.exec(event.data);
            $($._preload.audio).play(parts[1], function() {
                $($._preload.audio).dequeue('fx');
                event.source.postMessage('DEQUEUE', ['*']);
            });
        } else if (/^DEQUEUE$/.test(event.data)) {
            console.log("CHILD", event.data);
            if ($._preload.queued.length > 0) {
                $._preload.queued.shift().dequeue('fx');
            }
        } else if (/^PURGE$/.test(event.data)) {
            console.log("PARENT", event.data);
            // Delete all but the currently playing buffer to free up memory:
            for (id in $._preload.loaded) {
                if ($._preload.playingAudio != id) {
                    delete $._preload.loaded[id];
                }
            }
            // Clear all jQuery-queues (mainly the default 'fx' queue):
            $($._preload.audio).clearQueue();
            // Stop any currently playing sound:
            if (typeof $._preload.source !== "undefined") {
                $._preload.source.noteOff(0);
                clearTimeout($._preload.endedTimeout);
            } else if (typeof $._preload.audio !== "undefined"
                       && typeof $._preload.audio.stop === "function") {
                $._preload.audio.stop();
            }
        }
    }
}, false);

jQuery(function($) {

    // Init:
    $._preload = {
        requireTouchStart:
            (navigator.userAgent.match(/(iPad|iPhone|iPod|Android)/g) ? true : false),
        audio: document.createElement('audio'),
        context: createAudioContext(),
        formats: {},
        loaded: {},
        processing: {},
        queued: [],
        playingAudio: undefined
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

    // Fix broken audio tag with a mock:
    if (!(typeof $._preload.audio.play === 'function')) {
        $._preload.audio.play = function() { $(this).trigger('ended'); };
    }
    if (!(typeof $._preload.audio.load === 'function')) {
        $._preload.audio.load = function() {};
    }

    // Free memory by clearing the buffers from the previous games:
    if (!isMaster) {
        try { window.parent.postMessage('PURGE', ['*']); } catch (e) {}
    }

    $.extend({
        preload: function(id, uri, callback) {
            if (isMaster === false) {
                parent.window.postMessage('PRELOAD:' + id + ':' + uri, ['*']);
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
                    console.log('COMPLETE:', id, url);
                    delete $._preload.processing[id];
                    $._preload.loaded[id] = url;

                    if (jQuery.isEmptyObject($._preload.processing)) {
                        if ($._preload.requireTouchStart === true) {
                            console.log('IOS AUDIO DETECTED');
                            $('<div></div>').css({
                                'position': 'absolute',
                                'top': '0', 'right': '0',
                                'bottom': '0', 'left': '0',
                                'z-index': '99999'
                            }).bind('touchstart',function () {
                                $._preload.audio.load();
                                $._preload.requireTouchStart = false;
                                $(this).remove();
                                console.log('IOS AUDIO ACTIVATED');

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
                }});
            };

            var initAudioContext = function (url) {
                var saveBuffer = function(buffer) {
                    console.log('COMPLETE:', id, url);

                    delete $._preload.processing[id];
                    $._preload.loaded[id] = buffer;

                    if (jQuery.isEmptyObject($._preload.processing)) {
                        if ($._preload.requireTouchStart === true) {
                            console.log('IOS AUDIO DETECTED');
                            $('<div></div>').css({
                                'position': 'absolute',
                                'top': '0', 'right': '0',
                                'bottom': '0', 'left': '0',
                                'z-index': '99999'
                            }).bind('touchstart',function () {
                                $._preload.source =
                                    $._preload.context.createBufferSource();
                                $._preload.source.connect(
                                    $._preload.context.destination);
                                $._preload.source.noteOn(0);
                                $._preload.requireTouchStart = false;
                                $(this).remove();
                                console.log('IOS AUDIO ACTIVATED');

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
                };

                var request = new XMLHttpRequest();
                request.open('GET', url, true);
                request.responseType = 'arraybuffer';
                request.onload = function () {
                    //noinspection JSUnresolvedFunction
                    $._preload.context.decodeAudioData(request.response,
                                                       saveBuffer, function() {
                        /* OnError */
                    });
                };
                request.send();
            };

            for (i = 0; i < urls.length; i++) {
                if (urls[i].search(/mp3/i) > 0 && $._preload.formats['mp3']) {
                    if ($._preload.context) {
                        initAudioContext(urls[i]);
                    } else {
                        initAudio(urls[i]);
                    }
                    break;
                }
                if (urls[i].search(/ogg/i) > 0 && $._preload.formats['ogg']) {
                    if ($._preload.context) {
                        initAudioContext(urls[i]);
                    } else {
                        initAudio(urls[i]);
                    }
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
                    $._preload.playingAudio = id;

                    // Play using AudioContext:
                    if($._preload.context) {
                        // Play:
                        if (typeof $._preload.source !== "undefined") {
                            $._preload.source.disconnect();
                            delete $._preload.source;
                        }
                        $._preload.source =
                            $._preload.context.createBufferSource();
                        $._preload.source.connect(
                            $._preload.context.destination);
                        $._preload.source.buffer = audio;
                        $._preload.source.noteOn(0);

                        // Completion frees the queue:
                        if (typeof callback === 'function') {
                            $._preload.endedTimeout = setTimeout(function() {
                                callback()
                            }, audio.duration * 1000);
                        } else {
                            $._preload.endedTimeout = setTimeout(function() {
                                that.dequeue('fx');
                            }, audio.duration * 1000);
                        }
                    // Play using Audio-tag:
                    } else {
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
                                try {
                                    $._preload.audio.removeAttribute("src");
                                } catch (e) {}
                                callback();
                            } else {
                                try {
                                    $._preload.audio.removeAttribute("src");
                                } catch (e) {}
                                that.dequeue('fx');
                            }
                        });

                        // Play:
                        if (audio !== null && audio !== undefined) {
                            $._preload.audio.src = audio;
                            $._preload.audio.play();
                        }
                    }
                });
            } else if (id !== null && id !== undefined) {
                return this.queue('fx', function() {
                    $._preload.queued.push(that);
                    window.parent.postMessage('PLAY:' + id, ['*']);
                });
            } else {
                console.trace();
                return this;
            }
        }
    });
});

}).call(this);
