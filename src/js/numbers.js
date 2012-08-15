

$(document).ready(function(){
  newGame();
});

function newGame() {
  $('#answerLine').children().remove();
  $.get(global.ctx + '/rest/get/game/2/user/0', function(data){
    var jsdata = jQuery.parseJSON(data);
    var level = jsdata.level;
      $('#level span').text(level);
    var items = jsdata.items;
    console.log('new game '+data);
    var f = newGame;
    GameInitialize(items, {
      newGame: f
    });
    var i = 0;
    for (i=0; i<items.length; i++) {
	var nro = $('<span>'+items[i]+'</span>');
	nro.hide();
	$('#answerLine').append(nro);
	nro.delay(1000*i).fadeIn(500);
    }
    $(".blink").promise().done(function() {
      setupGame();
    });
  });
}

function setupGame() {
  $('.numberBtn').unbind('click');
  $('.numberBtn').click(function(event){
    console.log('click..');
    event.preventDefault();
    $(this).hide();
    $(this).fadeIn(500);
    var idx = $(this).text();
    console.log(idx);
    $(this).promise().done(function() {
      GameCheckUserPress(idx);
    });
  });
}


