jQuery(function($) {
    var checkWindowHeight, createGameFrame,
        timeout = null, dialog = null;

    checkWindowHeight = function() {
        timeout = null;

        var windowHeight = $(window).height(),
            platform = {
                "Windows": "windows",
                "iPad": "ipad"
            }[BrowserDetect.OS] || "windows";
        if (windowHeight < 768) {
            if (dialog === null) {
                // TODO: Create different instructions for different systems
                // and check the system from BrowserDetect.OS
                dialog = $.modal($('#fullscreen-' + platform).clone()
                    .css('display', 'block')
                    .one("touchstart", function() {
                        // "Accidentally" Activate iOS audio
                        if ($._preload !== undefined) {
                            if($._preload.iOS === true && $._preload.context) {
                                $._preload.source =
                                    $._preload.context.createBufferSource();
                                $._preload.source.connect(
                                    $._preload.context.destination);
                                $._preload.source.noteOn(0);
                                $._preload.iOS = false;
                            } else if ($._preload.iOS === true) {
                                $._preload.audio.play();
                                $._preload.iOS = false;
                            }
                        }
                        return true;
                    }), {
                    fitViewport: true,
                    closeOverlay: false,
                    closeSelector: ".pure-button-primary",
                    closeKeyCode: null,
                    closeText: ''
                });
                $(window.document).one('modalAfterClose', function() {
                    if (timeout !== undefined && timeout !== null) {
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
                var contentType = jqXHR.getResponseHeader("Content-Type");
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

    checkWindowHeight();


    function doOnOrientationChange()
    {
        $('head meta[name="viewport"]').remove();
        switch(window.orientation) 
        {  
        case -90:
        case 90:
        case 180: // lanscape
            $('head').append($('<meta name="viewport" content="height=768, width=device-width, initial-scale=0.9, user-scalable=no">'));
            break;
        default: // portrait
            $('head').append($('<meta name="viewport" content="height=device-height, width=768, initial-scale=1.0, user-scalable=no">'));
            break;
        }
    }

    window.addEventListener('onorientationchange', doOnOrientationChange);
    doOnOrientationChange();
});
