var global = global || {}
global.userid = 0;
global.gameItems = [];
global.userItems = [];
global.ctx = $('meta[name=context]').attr("content");
global.callbacks = {
    newGame: function(){},
    answerRight: function(rightItem){},
    answerWrong: function(rightItem, wrongItem){}
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
  $("body").off("click", "#next");

  global.gameItems = items;
  global.userItems = [];

    for (cb in callbacks) {
      global.callbacks[cb] = callbacks[cb];
    }
}

function GameCheckUserPress(item) {
  var currentIdx = global.userItems.length;
  if (global.gameItems[currentIdx] == item) {
    global.userItems.push(item)
    global.callbacks.answerRight(item);
  } else {
    global.callbacks.answerWrong(global.gameItems[currentIdx], item);
    GameIncorrectAnswer();
  }

  if (global.gameItems.length === global.userItems.length)
    GameCorrectAnswer();
}

function createDialog(data){
  var dialog;
  if ($('.modal').length === 0) {
    dialog = $('body').append($(data).filter('.modal')).find('.modal');
    dialog.find('.btn').click(function(event) {
      dialog.modal('hide');
    });
    dialog.on('hidden', function(event) {
      dialog.remove();
      global.callbacks.newGame();
    });
    dialog.modal('show');
  }
}

function GameCorrectAnswer() {
  $.get(global.ctx + '/pass', function(data) { createDialog(data); });
}

function GameIncorrectAnswer() {
  $.get(global.ctx + '/fail', function(data) { createDialog(data); });
}
