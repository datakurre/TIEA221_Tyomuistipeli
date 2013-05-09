var global = global || {};


// TODO move to library.
if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

function startMusic() {
    var mois = 'hei heippa moikka moi morjens'.split(' ');
    var moi = mois[Math.floor(Math.random()*mois.length)];
    $.preload('moi',
          global.ctx + '/snd/'+moi+'.[mp3,ogg]');
    $.preload('sudit',
          global.ctx + '/snd/Pelit_ja_Pensselit_by_Ahti_Laine.[mp3,ogg]');
    $('body').on('preloaded', function(){
	console.log($('<div></div>').snd('moi'));
	$('<div></div>').snd('sudit')[0].volume = 0.3;
	$('<div></div>').play('moi').play('sudit');
    });
}

function animateTitle() {
    var title = $('h1').text(), idx;
    var newTitle = '';
    for (idx=0; idx<title.length; idx+=1) {
        newTitle += '<div class="color-'+(idx%5)+'">'+title.charAt(idx) +'</div>';
    }
    $('h1').html(newTitle);
    $('h1').children().each(function(idx){
    var x = Math.PI * (idx-(title.length-1)/2)/title.length;
        $(this)
            .delay(400+idx*300)
            .animate({'top':'-80px'}, 300)
            .animate({'top':(30*Math.cos(x))+'px'}, 400+idx*50);
    });
}

function addPlayerButtons() {

    $('#mainView > .player').remove();

    var players = $.cookie('players');
    if (players == null) return;
    players = $.parseJSON(players).reverse();
    for (idx in players) {
        if (players[idx].name != "Vieras") {
            var btn = $('#buttonTemplate a').clone();
            btn.find('#name').text(players[idx].name);
            btn.attr('data-player', players[idx].id);
            $("#mainView").prepend(btn);
            btn.show();
            btn.click(function(event){
                $.cookie('active_player',
                         $(this).data('player'),
                         { expires: 365, path: '/'});
            });
        }
    }
}


$(document).ready(function() {

    startMusic();
    animateTitle();

    addPlayerButtons();

    // show current view
    $(window).bind('hashchange', function() {
        var hash = location.hash.toString();
        if (hash.startsWith('#liity')) {
            $('#joinView').slideDown();
            $('#mainView').slideUp();
        } else {
            $('#joinView').slideUp();
            $('#mainView').slideDown();
            addPlayerButtons();
        }
    });

    var handleSubmit = function(event) {

        event.preventDefault();
        $.post('liity',
               $('#joinData').serialize(),
               function(data) {
                   // Store information to server and create local
                   // data in cookie.
                   var players = $.cookie('players');
		   
                   if (players == null || players === undefined)
                       players = [];
                   else
                       players = $.parseJSON(players);

                   players.push({
                       'name': $('#joinData input[name="name"]').val(),
                       'id': data.id
                   });
		   
                   $.cookie('players',
                            JSON.stringify(players),
                            { expires: 365 });
		   
                   location.hash = '';
               });
    };
    $('#join').click(handleSubmit);
    $('#joinData').keypress(function(event) {
        if (event.which == 13) {
            event.preventDefault();
            handleSubmit(event);
            return false;
        }
    });
    $('#kokeile').click(function(event) {
        event.preventDefault();
        if ($.cookie('guest_player') !== null
            && $.cookie('guest_player') !== undefined) {
            $.cookie('active_player',
                     $.cookie('guest_player'),
                     { expires: 365 });
            window.location.href = global.ctx + '/pelaa';
        } else {
            $.post('kokeile', function(data) {
                $.cookie('guest_player',
                         data.id,
                         { expires: 365 });
                $.cookie('active_player',
                         data.id,
                         { expires: 365 });
                window.location.href = global.ctx + '/pelaa';
            });
        }
    });

    // trigger view!
    $(window).trigger('hashchange');
});
