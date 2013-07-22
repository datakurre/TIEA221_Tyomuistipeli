var global = global || {};

global.userid = 0;
global.gameItems = [];
global.userItems = [];
global.base_ctx = $('meta[name=base]').attr("content");
global.ctx = $('meta[name=context]').attr("content");
global.callbacks = {
    newGame: function(){},
    answerRight: function(rightItem){},
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





/* items = [ numbers ]
 */
function GameInitialize(items, callbacks) {
  // TODO remove this
  $("body").off("click", "#next");

  $('#game').css('display', 'block');

  global.gameItems = items;
  global.userItems = [];

    for (cb in callbacks) {
      global.callbacks[cb] = callbacks[cb];
    }
}



function GameCheckUserPress(item) {
  var currentIdx = global.userItems.length;
  global.userItems.push(item)
  if (global.gameItems[currentIdx] == item) {
    global.callbacks.answerRight(item);
  } else {
    global.callbacks.answerWrong(global.gameItems[currentIdx], item, GameIncorrectAnswer);
    //GameIncorrectAnswer();
    return;
  }

  if (global.gameItems.length === global.userItems.length)
    GameCorrectAnswer();
}


function GameCheckUserPressForSet(item) {
  global.userItems.push(item)
  if ($.inArray(item, global.gameItems) >= 0) {
    global.callbacks.answerRight(item);
  } else {
    global.callbacks.answerWrong(global.gameItems, item, GameIncorrectAnswer);
    //GameIncorrectAnswer();
    return;
  }

  if (global.gameItems.length === global.userItems.length)
    GameCorrectAnswer();
}

function GamePlayFeedback(passed, afterMusicAction) {
    var name = '';
    if (passed) {
	rights = [];
	for (var i=1; i<=15; i++) {
	    rights.push('right'+i);
	}
	name = rights[Math.floor(Math.random() * rights.length)];
    } else {
	wrongs = [];
	for (var i=1; i<=12; i++) {
	    wrongs.push('wrong'+i);
	}
	name = wrongs[Math.floor(Math.random() * wrongs.length)];
    }

    $.preload(name, global.base_ctx + '/snd/' + name + '.[mp3,ogg]');
    $('body').one('preloaded', function() {
	$('body').play(name).promise().done(function() { 
            afterMusicAction();
        });
    });
}

function createDialog(data){
  var dialog;
  if ($('.modal').length === 0) {
    dialog = $('body').append($(data).filter('.modal')).find('.modal');
    // dialog.find('.btn').click(function(event) {
    //   event.preventDefault();
    //   dialog.modal('hide');
    // });
    // dialog.on('hidden', function(event) {
    //   dialog.remove();
    //   global.callbacks.newGame();
    // });
    dialog.modal('show');
  }
}

function GameAnswerDialogShowButton() {
    $('.btn').removeAttr('disabled').animate({opacity: 1}, 500);
}

function GameCorrectAnswer() {
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

// Wire up jquery.rs.modal for each a[data-toggle='modal']:
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
