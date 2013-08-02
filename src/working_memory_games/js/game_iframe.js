jQuery(function($) {
    var checkWindowHeight, createGameFrame, updateViewport,
        timeout = null, dialog = null;

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

    updateViewport = function() {
        $('head meta[name="viewport"]').remove();
        switch(window.orientation) {
            case -90:
            case 90:
            case 180: // Landscape:
                $('head').append($('<meta name="viewport" content="height=768, width=device-width, initial-scale=0.9, user-scalable=no">'));
                break;
            default: // Portrait:
                $('head').append($('<meta name="viewport" content="height=device-height, width=768, initial-scale=1.0, user-scalable=no">'));
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
                        $._preload.source =
                            $._preload.context.createBufferSource();
                        $._preload.source.connect(
                            $._preload.context.destination);
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
