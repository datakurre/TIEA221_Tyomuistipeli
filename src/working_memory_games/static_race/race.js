function newGame() {
  $('.carmask').css('opacity', '1.0');
  $('.carmask').hide();
  $.get(global.ctx + '/new', function(data){
    var level = data.level;
      $('#level span').text(level);
    var items = data.items;
    console.log('new game '+data);
    var f = newGame;
    GameInitialize(items, {
      newGame: f
    });
    var masks = { };
    $('.carmask').each(function(){
      masks[$(this).attr('id')] = $(this);
    });
    var delays = {};
    for (id in masks) {
      delays[id] = -1;
    }
    var i = 0;
    for (i=0; i<items.length; i++) {
      var id = 'car'+items[i];
      var delay = 1000*i;
      if (delays[id] >= 0)
        delay = (i - delays[id] - 1)*1000;
      delays[id] = i;
      masks[id] = masks[id].delay(delay).fadeIn(500).fadeOut(500);
    }
    $(".carmask").promise().done(function() {
      setupGame();
    });
  });
}

function setupGame() {
  $('.carmask').css('display', 'block');
  $('.carmask').css('opacity', '0');

  $('.carmask').unbind('mousedown');
  $('.carmask').mousedown(function(event){
    event.preventDefault();
  });
  $('.carmask').unbind('click');
  $('.carmask').click(function(event){
      console.log('click..');
    event.preventDefault();
    $(this).css('display', 'block');
    $(this).css('opacity', '1');

    var idx = $(this).attr('id').substring(3);
    $(this).fadeOut(500);
    $(this).promise().done(function() {
      $(this).css('display', 'block');
      $(this).css('opacity', '0');
      GameCheckUserPress(idx);
    });
  });
}


$(document).ready(function(){
  newGame();
});
