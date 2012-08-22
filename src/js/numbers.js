

$(document).ready(function(){
  newGame();
});


function newGame() {
  global.loader = html5Preloader();
  $('.numberBtn').unbind('click');
  $('#answerLine').children().remove();
  $.get(global.ctx + '/rest/get/game/2/user/0', function(data){
    var jsdata = jQuery.parseJSON(data);
    var level = jsdata.level;
      $('#level span').text(level);
    var items = jsdata.items;
    console.log('new game '+data);

    GameInitialize(items, {
      newGame: newGame,
      answerRight: answerRight,
      answerWrong: answerWrong
    });

    var sounds = {};
    var i = 0;
    for (i=0; i<items.length; i++) {
	var nro = items[i];
	sounds['snd'+nro+'*:'+global.ctx+'/snd/'+nro+'.ogg||'+global.ctx+'/snd/'+nro+'.mp3'] = nro;
    }
    files = [];
    for (f in sounds) files.push(f);
    console.log(files);
    global.loader.on('finish', function(){
      for (i=0; i<items.length; i++) {
	var nro = items[i];
          playSound(nro, i*1800);
      }
      setTimeout(setupGame, items.length*1700);
    });
    global.loader.on('error', function(e){ console.error(e); });
    //global.loader.on('fileloaded', function(e){ console.error(e); });
    global.loader.addFiles(files);


  });
}

function playSound(nro, delay) {
  setTimeout(function() {
    global.loader.getFile('snd'+nro).play();
  }, delay);
}

function setupGame() {
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

function answerRight(item) {
  var elm = $('<span class="rightNro" style="opacity:0.1;margin-left:200px;">'+item+'</span>');
  $('#answerLine').append(elm);
  elm.animate({
    opacity: 1,
    'margin-left': '5'
  }, 500, function() {
    // Animation complete.
  });
}

function answerWrong(right, item) {
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
    for (i=0;i<4;i++)
	elmRight = elmRight.animate({opacity: 0.3}, 'fast').animate({opacity: 1}, 'fast');
}
