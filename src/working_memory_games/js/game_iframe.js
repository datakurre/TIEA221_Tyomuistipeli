jQuery(function($) {
    var checkWindowHeight, createGameFrame, onGameFrameLoad, dialog = null;

    checkWindowHeight = function() {
        var windowHeight = $(window).height(),
            platform = {
                "Windows": "windows",
                "iPad": "ipad"
            }[BrowserDetect.OS] || "windows";
        if (windowHeight < 786) {
            if (dialog === null) {
                // TODO: Create different instructions for different systems
                // and check the system from BrowserDetect.OS
                dialog = $.modal($('#fullscreen-' + platform).clone()
                    .css('display', 'block'), {
                    fitViewport: true,
                    closeOverlay: false,
                    closeSelector: ".pure-button-primary",
                    closeKeyCode: null,
                    closeText: ''
                });
                $(window.document).one('modalAfterClose', createGameFrame);
            }
            window.setTimeout(checkWindowHeight, 500);  // check every 0.5 sec
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
                        .bind('load', onGameFrameLoad)
                        .prependTo($('body'));
                } else {
                    window.location = base_url + '#pelataan-taas-huomenna';
                }
            }
        });
    };

    onGameFrameLoad = function() {
        if (this.contentWindow !== undefined
                && this.contentWindow.location !== undefined
                && this.contentWindow.postMessage !== undefined) {
            this.contentWindow.postMessage(
                "CONNECT", this.contentWindow.location.toString());
        }
    };

    checkWindowHeight();
});
