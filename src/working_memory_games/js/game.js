/*

 Global and shared resources

 The only shared js resource between games. Provides shared global
 variables and API for loading and saving session bound game data.

*/

/* Define console polyfill: */
if (window.console === null || window.console === undefined) {
    //noinspection JSValidateTypes,JSUnusedGlobalSymbols
    window.console = {
        log: function() {},
        trace: function() {}
    };
}

/* Define globals: */
var global = global || {};

global.userid = 0;
global.gameItems = [];
global.userItems = [];
global.base_ctx = $('meta[name=base]').attr("content");
global.ctx = $('meta[name=context]').attr("content");

//noinspection JSUnusedGlobalSymbols
global.callbacks = {
    newGame: function() {},
    answerRight: function(rightItem) {},
    answerWrong: function(rightItem, wrongItem, continueFunc) {
        continueFunc();
    }
};

$.getDocHeight = function(){
    return Math.max(
        $(document).height(),
        $(window).height(),

        /* For opera: */
        document.documentElement.clientHeight
    );
};


/* items = [ numbers ] */
function GameInitialize(items, callbacks) {
    // TODO remove this
    $("body").off("click", "#next");

    $('#game').css('display', 'block');

    global.gameItems = items;
    global.userItems = [];

    for (var cb in callbacks) {
        if (callbacks.hasOwnProperty(cb)) {
            global.callbacks[cb] = callbacks[cb];
        }
    }
}


function GameCheckUserPress(item) {
    var currentIdx = global.userItems.length;
    global.userItems.push(item);

    if (global.gameItems[currentIdx] == item) {
        global.callbacks.answerRight(item);
    } else {
        global.callbacks.answerWrong(global.gameItems[currentIdx], item, GameIncorrectAnswer);
        //GameIncorrectAnswer();
        return;
    }

    if (global.gameItems.length === global.userItems.length) {
        GameCorrectAnswer();
    }
}


//noinspection JSUnusedGlobalSymbols
function GameCheckUserPressForSet(item) {
    // only add to selection set if not added already
    if ($.inArray(item, global.userItems) < 0) {
        global.userItems.push(item);
    }
    if ($.inArray(item, global.gameItems) >= 0) {
        global.callbacks.answerRight(item);
    } else {
        global.callbacks.answerWrong(global.gameItems, item, GameIncorrectAnswer);
        //GameIncorrectAnswer();
        return;
    }

    if (global.gameItems.length === global.userItems.length) {
        GameCorrectAnswer();
    }
}

function GamePlayFeedback(passed, afterMusicAction) {
    var name = '', rights = [], wrongs = [], i;

    if (passed) {
        for (i = 1; i <= 1; i++) {
            rights.push('right' + i);
        }
        name = rights[Math.floor(Math.random() * rights.length)];
    } else {
        for (i = 1; i <= 1; i++) {
            wrongs.push('wrong' + i);
        }
        name = wrongs[Math.floor(Math.random() * wrongs.length)];
    }

    $.preload(name, global.base_ctx + '/snd/' + name + '.[mp3,ogg]');

    $('body').one('preloaded', function() {
        //noinspection JSUnresolvedFunction
        $('body').play(name).promise().done(function() {
            afterMusicAction();
        });
    });
}

function createDialog(data){
    var dialog;
    if ($('.modal').length === 0) {
        dialog = $('body').append($(data).filter('.modal')).find('.modal');
        dialog.modal('show');

        GameRaiseCurtain();
    }
}

function GameAnswerDialogShowButton() {
    $('.btn').removeAttr('disabled').animate({opacity: 1}, 500);
}

function GameDropCurtain() {
    if ($('.modal-backdrop.curtain').length === 0) {
        $('body').append('<div class="modal-backdrop curtain"></div>');
    }
}

function GameRaiseCurtain() {
    $('.modal-backdrop.curtain').remove();
}

function GameCorrectAnswer() {
    GameDropCurtain();

    $.ajax({
        type: 'POST',
        url: global.ctx + '/pass',
        data: JSON.stringify({game: global.gameItems, user: global.userItems}),
        contentType: 'application/json; charset=utf-8',
        success: function(data) {
            GamePlayFeedback(true, GameAnswerDialogShowButton);
            createDialog(data);
        }
    });
}

function GameIncorrectAnswer() {
    GameDropCurtain();

    $.ajax({
        type: 'POST',
        url: global.ctx + '/fail',
        data: JSON.stringify({game: global.gameItems, user: global.userItems}),
        contentType: 'application/json; charset=utf-8',
        success: function(data) {
            GamePlayFeedback(false, GameAnswerDialogShowButton);
            createDialog(data);
        }
    });
}

/* Wire up jquery.rs.modal for each a[data-toggle='modal']: */
jQuery(function($) {
    $('a[data-toggle="modal"]').click(function(event) {
        var target = $(this).attr('href'),
            content = $(target).clone().css('display', 'block');
        event.preventDefault();
        $.modal(content, {
            fitViewport: true,
            closeSelector: '.pure-button-primary',
            closeText: ''
        });
    });
});
