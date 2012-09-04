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

function createDlg(data){
  console.log('create dlg');
  if ($('#overlay').length === 0) {
    $('body').append(data);
    $('#shader').css('width', window.innerWidth+'px');
    $('#shader').css('height', $.getDocHeight()+'px');
    $('#shader').css('left', ((768-window.innerWidth)/2)+'px');

    $('#dialog').animate({'opacity':'1.0'}, 500);
    $('#shader').animate({'opacity':'0.6'}, 500);

    $('#next').click(function(event){
	event.preventDefault();
	$('#dialog').fadeOut();
	$('#shader').fadeOut().promise().done(function() {
	    $('#overlay').remove();
	    global.callbacks.newGame();
	});
    });
  }
}
function GameCorrectAnswer() {
  $.get(global.ctx + '/rest/game/done/user/'+global.userid, function(data){
      createDlg(data);
  });
}

function GameIncorrectAnswer() {
  $.get(global.ctx + '/rest/game/incorrect/user/'+global.userid, function(data){
      createDlg(data);
  });
}
