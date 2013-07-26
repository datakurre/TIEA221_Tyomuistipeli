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
        context: (function() {
            if (window.webkitAudioContext !== undefined) {
               return new webkitAudioContext();
            } else { return undefined; }
        })(),
        formats: {},
        loaded: {},
        processing: {},
        queued: []
    };

    $._preload.source = $._preload.context.createBufferSource();
    $._preload.source.connect($._preload.context.destination);

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
    if (!(typeof $._preload.audio.load === 'function')) {
        $._preload.audio.load = function() {};
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
            var initHTML5Audio = function(url) {
                console.log("HTML5AUDIO");
                var request = new XMLHttpRequest();
                request.open('GET', url, true);
                request.responseType = 'arraybuffer';

                request.onload = function() {
                    $._preload.context.decodeAudioData(request.response,
                                                       function(buffer) {
                        console.log('COMPLETE:', id, url);
                        console.log('COMPLETE:', buffer);
                        delete $._preload.processing[id];
                        $._preload.loaded[id] = buffer;

                        if (jQuery.isEmptyObject($._preload.processing)) {
                           if ($._preload.iOS === true) {
                               console.log('IOS AUDIO DETECTED');
                               $('<div></div>').css({
                                   'position': 'absolute',
                                   'top': '0', 'right': '0',
                                   'bottom': '0', 'left': '0',
                                   'z-index': '99999'
                               }).bind('touchstart', function() {
                                       console.log('IOS AUDIO ACTIVATED');
                                       $(this).remove();
                                       $._preload.iOS = false;
                                       $._preload.audio.load();
                                       $._preload.source.noteOn(0);
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
                    }, function() {
                       /* OnError */
                    });
                };
                request.send();
            }
            var initAudio = function(url) { return $.ajax({
                type: 'get',
                url: url,
                beforeSend: function(jqXHR) {
                    if (navigator.userAgent.match(/(iPad|iPhone|iPod)/g)
                        && typeof window.btoa === 'function') {
                        jqXHR.overrideMimeType(
                            'text/plain; charset=x-user-defined');
                    }
                },
                complete: function(jqXHR) {
                    var data, i;

                    console.log('COMPLETE:', id, url);
                    delete $._preload.processing[id];
                    $._preload.loaded[id] = url;

                    if (navigator.userAgent.match(/(iPad|iPhone|iPod)/g)
                        && typeof window.btoa === 'function') {
                        data = new ArrayBuffer(jqXHR.responseText.length);
                        for (i = 0; i < jqXHR.responseText.length; i++ ) {
                            data[i] = String.fromCharCode(
                                jqXHR.responseText[i].charCodeAt(0) & 0xff);
                        }
                        $._preload.loaded[id] =
                            'data:audio/mpeg;base64,' + btoa(data);

                        $._preload.loaded[id] = btoa(data);
                    }

                    if (jQuery.isEmptyObject($._preload.processing)) {
                        if ($._preload.iOS === true) {
                            console.log('IOS AUDIO DETECTED');
                            $('<div></div>').css({
                                'position': 'absolute',
                                'top': '0', 'right': '0',
                                'bottom': '0', 'left': '0',
                                'z-index': '99999'
                            }).bind('touchstart', function() {
                                console.log('IOS AUDIO ACTIVATED');
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
                    if (navigator.userAgent.match(/(iPad|iPhone|iPod)/g)) {
                        initHTML5Audio(urls[i]);
                    } else {
                        initAudio(urls[i]);
                    }
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
//                        $._preload.audio.src = audio;
//                        $._preload.audio.play();
                        $._preload.source.disconnect();
                        delete $._preload.source;

                        $._preload.source = $._preload.context.createBufferSource();
                        $._preload.source.connect($._preload.context.destination);
                        $._preload.source.buffer = audio;
                        $._preload.source.noteOn(0);

                        setTimeout(function() { callback();
                          console.log('playback finished');
                        }, audio.duration * 1000);
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
