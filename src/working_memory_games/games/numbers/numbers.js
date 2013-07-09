
$(document).ready(function(){

  $.preload('kuulet_numeroita',
            global.ctx + '/snd/kuulet_numeroita.[ogg,mp3]');
  $.preload('toista',
            global.ctx + '/snd/toista_numerot.[ogg,mp3]');
  for (var i=1; i<10; i++) {
    $.preload('normal_'+i, global.ctx + '/snd/normal_' + i + '.[ogg,mp3]');
    $.preload('adapt_'+i+'_0', global.ctx + '/snd/adapt_' + i + '_0.[ogg,mp3]');
    $.preload('adapt_'+i+'_1', global.ctx + '/snd/adapt_' + i + '_1.[ogg,mp3]');
    $.preload('adapt_'+i+'_2', global.ctx + '/snd/adapt_' + i + '_2.[ogg,mp3]');
  }
  $('body').one('preloaded', function(){
    var query = location.search !== undefined? location.search: '';
    $.get(global.ctx + '/runanimation'+query, function(data){
	if (data.animation) {
	    runAnimation();
	} else {
	    newGame();
	}
    });
  });
});

function runAnimation() {
  console.log("animation here");
  newGame();
}

function newGame() {
  global.loader = html5Preloader();
  $('.numberBtn').unbind('click');
  $('#answerLine').children().remove();
  $.get(global.ctx + '/new', function(data){
    $('body').append('<div class="modal-backdrop curtain"></div>');
    var level = data.level;
      $('#level span').text(level);
    var items = data.items;
    console.log('new game '+data);

    GameInitialize(items, {
      newGame: newGame,
      answerRight: answerRight,
      answerWrong: answerWrong
    });

    var sounds = {};
    var i = 0;

    if (data.try == 0) { // first time
      $('body').play('kuulet_numeroita');
    } else {
      $('body').play('toista');
    }

    for (var i in data.items) {
      if (data.assisted) {
        $('body').play('adapt_'+data.items[i]+'_'+(i % 3));
      } else { // normal non-assisted
        $('body').play('normal_'+data.items[i]);
      }
    }
    $('body').promise().done(function(){
      setupGame();
    });
  });
}

function setupGame() {
  $('.modal-backdrop.curtain').remove();
  $('.numberBtn').unbind('mousedown');
  $('.numberBtn').mousedown(function(event){
    event.preventDefault();
  });


  $('.numberBtn').click(function(event){
    console.log('click..');
    event.preventDefault();
    $(this).hide();
    $(this).fadeIn(500);
    var idx = $(this).text();
    console.log(idx);

    GameCheckUserPress(idx);
  });
}

function kavenna() {
  var existing = $('.rightNro');
  existing.each(function(idx){
    if (idx < existing.length-1) {
      $(this).animate({'width': '15px'}, 500);
    }
  });
}

function answerRight(item) {
  kavenna();

  var elm = $('<span class="rightNro" style="opacity:0.1;margin-left:200px;">'+item+'</span>');
  $('#answerLine').append(elm);
  elm.animate({
    opacity: 1,
    'margin-left': '5'
  }, 500, function() {
    // Animation complete.
  });
}

function answerWrong(right, item, continueFunc) {
  kavenna();

  var elm = $('<span class="wrongNro" style="opacity:0.1;margin-left:200px;">'+item+'</span>');
  $('#answerLine').append(elm);
  elm.animate({
    opacity: 1,
    'margin-left': '5'
  }, 500);

  var elmRight = $('<span class="rightNro" style="opacity:0.1;margin-left:200px;">'+right+'</span>');
  $('#answerLine').append(elmRight);
  elmRight = elmRight.animate({
    opacity: 1,
    'margin-left': '5'
  }, 500);
    var i;
    for (i=0;i<4;i++) {
      elmRight = elmRight.animate({opacity: 0.3}, 'fast').animate({opacity: 1}, 'fast');
    }
    elmRight.promise().done(function(){
        continueFunc();
    });
}
