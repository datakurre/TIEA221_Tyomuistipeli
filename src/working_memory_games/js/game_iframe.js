/*

  Browser frame manager and game loader

  Creates game frames so that the game levels can be loaded into iframe and
  they can share the same main frame (which allows to re-use the main frames
  permission for playing audio on mobile devices with lib/jquery.snd.js).

*/
jQuery(function($) {
    var checkWindowHeight, createGameFrame, updateViewport,
        timeout = null, dialog = null;

    // Check window height and warn if too small
    checkWindowHeight = function() {
        var windowHeight = $(window).height(),
            platform = {
                'Windows': 'windows'
            }[BrowserDetect.OS] || 'windows';

        if (windowHeight < 768) {
            if (dialog === null) {
                dialog = $.modal($('#fullscreen-' + platform).clone()
                          .css('display', 'block'), {
                    fitViewport: true,
                    closeOverlay: false,
                    closeSelector: '.pure-button-primary',
                    closeKeyCode: null,
                    closeText: ''
                });
                $(window.document).one('modalAfterClose', function() {
                    if (timeout !== null) {
                        timeout = null;
                        window.clearTimeout(timeout);
                    }
                    createGameFrame();
                });
            }
            timeout = window.setTimeout(checkWindowHeight, 500);
        } else if (dialog !== null) {
            dialog.close();
        } else {
            createGameFrame();
        }
    };

    // Create game iframe and load the next level in the game sessions
    createGameFrame = function () {
        var base_url = $('meta[name=base]').attr('content');
        $.ajax({
            type: 'POST',
            url: base_url + '/next_game',
            contentType: 'application/json; charset=utf-8',
            success: function(data, textStatus, jqXHR) {
                var contentType = jqXHR.getResponseHeader('Content-Type');
                if (/^application\/json.*/.test(contentType)) {
                    $('<iframe></iframe>')
                        .attr('id', 'game-iframe')
                        .attr('width', '100%')
                        .attr('height', '100%')
                        .attr('scrolling', 'no')
                        .attr('frameborder', '0')
                        .attr('src', base_url + '/' + data.game + '/')
                        .prependTo($('body'));
                } else {
                    window.location = base_url + '#pelataan-taas-huomenna';
                }
            }
        });
    };

    // Update viewport tag for mobile devices
    updateViewport = function() {
        var $head = $('head');
        $head.find('meta[name="viewport"]').remove();
        //noinspection JSUnresolvedVariable
        switch(window.orientation) {
            case -90:
            case 90:
            case 180: // Landscape:
                $head.append($('<meta name="viewport" content="height=768, width=device-width, initial-scale=0.9, user-scalable=no">'));
                break;
            default: // Portrait:
                $head.append($('<meta name="viewport" content="height=device-height, width=768, initial-scale=1.0, user-scalable=no">'));
                break;
        }
    };

    // Check windows height
    if (BrowserDetect.OS !== 'iPad') {
        checkWindowHeight();
    }

    // Limit setViewportOnRotation only for iPad, for which it is optimized:
    if (BrowserDetect.OS === 'iPad') {
        window.addEventListener('onorientationchange', updateViewport);
        updateViewport();
    }

    // Show big red button for iPad
    if (BrowserDetect.OS === 'iPad') {
        dialog = $.modal($('#touchstart').clone()
            .css('display', 'block')
            .one('touchstart', function() {
                if ($._preload !== undefined && $._preload.requireTouchStart) {
                    if ($._preload.context) {
                        //noinspection JSUnresolvedFunction
                        $._preload.source =
                            $._preload.context.createBufferSource();
                        //noinspection JSUnresolvedFunction,JSUnresolvedVariable
                        $._preload.source.connect(
                            $._preload.context.destination);
                        //noinspection JSUnresolvedFunction
                        $._preload.source.noteOn(0);
                    } else {
                        $._preload.audio.play();
                    }
                    $._preload.requireTouchStart = false;
                }
                return true;
            }), {
            width: 708,
            height: 566,
            fitViewport: true,
            closeOverlay: false,
            closeSelector: "#big-red-button",
            closeKeyCode: null,
            closeText: ''
        });
        $(window.document).one('modalAfterClose', function() {
            createGameFrame();
        });
    }
});
