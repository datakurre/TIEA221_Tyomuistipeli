/*
 * jQuery RS Modal v0.3.0
 * https://github.com/richardscarrott/jquery-modal/
 *
 * Copyright (c) 2012 Richard Scarrott
 * http://www.richardscarrott.co.uk
 *
 * Dual licensed under the MIT and GPL licenses:
 * http://www.opensource.org/licenses/mit-license.php
 * http://www.gnu.org/licenses/gpl.html
 *
 */
 
(function ($, undefined) {

    'use strict';

    // touch detection required to ensure viewport calculation returns 'CSS pixels'
    // via window.innerWidth instead of the virtual viewport dimension via window.outerWidth
    if (!$.support.touch) {
        $.support.touch = 'ontouchend' in document;
    }

    if (!$.rs) {
        $.rs = {};
    }

    $.rs.Modal = function (name, defaults) {
        if (!(this instanceof $.rs.Modal)) {
            throw new Error('$.rs.Modal() has been called without the \'new\' keyword.');
        }

        this.modalName = name;

        if (defaults) {
            this.defaults = $.extend({}, this.defaults, defaults);
        }
    };

    $.rs.Modal.prototype = {

        version: '0.3.0',

        isInitialized: false,

        isOpen: false,

        defaults: {

            // settings
            width: 'auto',
            height: 'auto',
            maxWidth: null,
            maxHeight: null,
            fitViewport: false,
            keepAspect: false,
            modal: true,
            openSpeed: 'fast',
            closeSpeed: 'fast',
            closeText: 'close X',
            className: null,
            overlayClassName: null,
            position: {}, // { top: 50, left: 50 }
            closeSelector: '.modal-content-close',
            closeKeyCode: 27, // Esc,
            closeOverlay: true,
            overlayOpacity: 0.5,

            // callbacks
            init: $.noop,
            beforeOpen: $.noop,
            afterOpen: $.noop,
            beforeClose: $.noop,
            afterClose: $.noop,
            afterResize: $.noop

        },

        _init: function (options) {
            this.options = $.extend({}, this.defaults, options);

            if (!this.isInitialized) {
                this._objects();
                this._events();
                this.options.init(this.objects);
                this.objects.doc.trigger('modalInit', [this.objects]);
                this.isInitialized = true;
            }
        },

        // creates and adds modal to DOM
        _objects: function () {
            this.objects = {};

            this.objects.modal = $('<div />', {
                'class': this.modalName
            });

            this.objects.content = $('<div />', {
                'class': this.modalName + '-content'
            })
            .appendTo(this.objects.modal);

            // NOTE: mobile safari requires close button to be anchor
            // (clickable element) because event is delegated
            this.objects.closeBtn = $('<a />', {
                href: '#',
                'class': this.modalName + '-close',
                text: this.options.closeText
            })
            .appendTo(this.objects.modal);

            this.objects.overlay = $('<div />', {
                'class': this.modalName + '-overlay'
            })
            .appendTo('body');

            this.objects.modal.appendTo('body');

            this.objects.win = $(window);
            this.objects.doc = $(document);
            this.objects.html = $('html');
        },

        _events: function () {
            var self = this,
                closeSelector = this.options.closeSelector ?
                    this.options.closeSelector + ', .' + this.modalName + '-close' : '.' + this.modalName + '-close',
                refreshEvent = $.support.touch ? 'orientationchange' : 'resize';

            this.objects.modal
                .delegate(closeSelector, 'click.' + this.modalName, function (e) {
                    e.preventDefault();

                    self.close();

                });

            this.objects.overlay
                .bind('click.' + this.modalName, function () {
                    if (self.options.closeOverlay) {
                        self.close();
                    }
                });

            this.objects.win
                .bind(refreshEvent + '.' + this.modalName, function () {
                    self.refresh();
                });

            this.objects.doc
                .bind('keyup.' + this.modalName, function (e) {
                    if (e.keyCode === self.options.closeKeyCode) {
                        self.close();
                    }
                });
        },

        // appends contents and opens modal
        open: function (content, options) {
            var self = this,
                speed;

            this._init(options);

            speed = this.isOpen ? 0 : this.options.openSpeed;

            this.objects.content.empty();

            if (content) {
                this.objects.content.append(content);
            }

            this._resetStyles();
            this._setIsOpen(false);

            this.objects.modal
                .removeClass()
                // add '.modal' back as it's been removed above (cannot just remove className, in cases where className has changed)
                .addClass(this.options.className ? this.modalName + ' ' + this.options.className : this.modalName)
                .css(this._getPosition());

            this.options.beforeOpen(this.objects);
            this.objects.doc.trigger('modalBeforeOpen', [this.objects]);
            this._setIsOpen(true);

            this.objects.modal.fadeIn(speed, function () {
                self.options.afterOpen(self.objects);
                self.objects.doc.trigger('modalAfterOpen', [self.objects]);
            });

            if (this.options.modal) {
                this._sizeOverlay();
                this.objects.overlay
                    .removeClass()
                    .addClass(this.options.overlayClassName ? this.modalName + '-overlay ' + this.options.overlayClassName : this.modalName + '-overlay')
                    .fadeTo(speed, this.options.overlayOpacity);
            }
        },

        _setIsOpen: function (val) {
            if (val) {
                this.isOpen = true;
                this.objects.html.addClass(this.modalName + '-isopen');
            }
            else {
                this.isOpen = false;
                this.objects.html.removeClass(this.modalName + '-isopen');
            }
        },

        // sets height of overlay to that of document, means it's no longer
        // relying on fixed positioning (touch devices + IE6) and body can
        // be height: 100%
        _sizeOverlay: function () {
            this.objects.overlay
                .height(this.objects.doc.height());
        },

        refresh: function () {
            if (this.isOpen) {

                this._resetStyles();
                this._setIsOpen(false);

                this.objects.modal
                    .css(this._getPosition())
                    .show();

                this._setIsOpen(true);

                if (this.options.modal) {
                    this._sizeOverlay();
                    this.objects.overlay
                        .css('opacity', this.options.overlayOpacity)
                        .show();
                }

                this.options.afterResize(this.objects);
                this.objects.doc.trigger('modalAfterResize', [this.objects]);
            }
        },

        // updates modal with new content, options will persist
        update: function (newContent, options) {
            if (this.isOpen) {
                this.open(newContent, $.extend(this.options, options));
            }
        },

        // helper method to indicate loading
        loading: function (beforeClose) {
            this.open(undefined, {
                className: this.modalName + '-isloading',
                beforeClose: beforeClose || $.noop
            });
        },

        close: function (animate) {
            var self = this,
                speed = animate || animate === undefined ? this.options.closeSpeed : 0;

            this.options.beforeClose(this.objects);
            this.objects.doc.trigger('modalBeforeClose', [this.objects]);

            this.objects.modal.fadeOut(speed, function () {

                self._resetStyles();
                self._setIsOpen(false);
                self.options.afterClose(self.objects);
                self.objects.doc.trigger('modalAfterClose', [self.objects]);

            });

            if (this.options.modal) {
                this.objects.overlay.fadeOut(speed);
            }
        },

        // removes all style attributes, NOTE: CSS should hide .modal by default
        _resetStyles: function () {
            this.objects.modal
                .add(this.objects.overlay)
                    .attr('style', '');
        },

        // return top, left, width and height of modal
        _getPosition: function () {

            //noinspection JSUnresolvedFunction,JSValidateTypes
            var options = this.options,
                top,
                left,
                width = options.width,
                height = options.height,
                maxWidth = options.maxWidth,
                maxHeight = options.maxHeight,
                oldWidth,
                oldHeight,
                boxModelWidth = this.objects.modal.outerWidth(true) - this.objects.modal.width(), // padding, border, margin
                boxModelHeight = this.objects.modal.outerHeight(true) - this.objects.modal.height(), // padding, border, margin
                viewport = {
                    x: ($.support.touch ? window.innerWidth : this.objects.win.width()) - boxModelWidth,
                    y: ($.support.touch ? window.innerHeight : this.objects.win.height()) - boxModelHeight
                },
                scrollPos = {
                    x: this.objects.doc.scrollLeft(),
                    y: this.objects.doc.scrollTop()
                },
                centreCoords = {
                    x: (viewport.x / 2) + scrollPos.x,
                    y: (viewport.y / 2) + scrollPos.y
                },
                h, // throwaway var to hold a height value
                w; // throwaway var to hold a width value

            // get natural height
            if (height === 'auto') {
                // ensure that if we set the width to maxWidth when calculating natural height
                // it's actually the smallest it'll ever be, i.e. the viewport might be smaller causing the content to be smaller
                w = maxWidth > viewport.x ? viewport.x : maxWidth;

                // if container width is auto or exceeds maxwidth set to maxwidth else set to container width
                this.objects.modal.width(maxWidth && width === 'auto' || maxWidth && width > maxWidth ? w : width);
                height = this.objects.modal.height();
                this.objects.modal.width('');
            }

            // get natural width
            if (width === 'auto') {
                h = maxHeight > viewport.y ? viewport.y : maxHeight;
                // we know here that height will bo longer be 'auto'
                this.objects.modal.height(maxHeight && height > maxHeight ? h : height);
                width = this.objects.modal.width();
                this.objects.modal.height('');
            }

            // set old width to then calculate aspect (before it possibly gets skewed by maxwidth and maxheight)
            oldWidth = width;
            oldHeight = height;

            // check maxWidth and maxHeight
            width = maxWidth && width > maxWidth ? maxWidth : width;
            height = maxHeight && height > maxHeight ? maxHeight : height;

            // check modal fits in viewport
            if (options.fitViewport) {
                width = width > viewport.x ? viewport.x : width;
                height = height > viewport.y ? viewport.y : height;
            }

            // check aspect ratio
            if (options.keepAspect) {
                h = height; // current height

                height = oldHeight * width / oldWidth;

                // if h is greater than height then adjust width instead
                if (height > h) {
                    width = oldWidth * h / oldHeight;
                    height = h;
                }
            }

            // set coords
            top = this.options.position.top !== undefined ? this.options.position.top : centreCoords.y - (height / 2);
            left = this.options.position.left !== undefined ? this.options.position.left : centreCoords.x - (width / 2);

            // check popup doesn't display outside of document
            if (!options.fitViewport) {
                top = top < scrollPos.y ? scrollPos.y : top;
                left = left < scrollPos.x ? scrollPos.x : left;
            }

            return {
                width: width,
                height: height,
                top: top,
                left: left
            };
        },

        // removes modal from DOM
        destroy: function () {
            this.objects.win.unbind('.' + this.modalName);
            this.objects.doc.unbind('.' + this.modalName);
            this.objects.modal.remove();
            this.objects.overlay.remove();
            this._setIsOpen(false);
            delete this.objects;
            delete this.options;
        }
    };

    $.modal = function(content, options) {
        return (new $.rs.Modal('modal', options)).open(content); };

})(jQuery);

// Wire up jquery.rs.modal for each a[data-toggle='modal']:
jQuery(function($) {
    $('a[data-toggle="modal"]').click(function(event) {
        var target = $(this).attr('href'),
            content = $(target).clone().css('display', 'block');
        event.preventDefault();
        $.modal(content, {
            fitViewport: true,
            closeText: ''
        });
    });
});
