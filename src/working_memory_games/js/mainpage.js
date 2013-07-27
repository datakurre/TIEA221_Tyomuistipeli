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

    // Init local variables
    var players, $buttons = {}, idx, player, btn;

    // Remove any existing button;
    $('#mainView > .player').remove();

    // Get available players from cookie
    players = $.cookie('players');

    // When cookie was not found, do nothing
    if (players === null || players === undefined) { return; }

    // Otherwise, parse cookie and add player buttons:w
    players = $.parseJSON(players).reverse();
    for (idx in players) {
        player = players[idx];

        if (player.guest !== true) {
            btn = $('#buttonTemplate a').clone();
            btn.find('.name').text(player.name);
            btn.attr('data-player', player.id);
            $("#mainView").prepend(btn);
            btn.show();
            btn.click(function() {
                $.cookie('active_player',
                         $(this).data('player'),
                         { expires: 365, path: '/'});
            });
            $buttons[player.id] = btn;
        }
    }

    if (players.length > 0) {
        $.post('session_status', function(data) {
            var player_id, session_status;
            for (player_id in data) {
                session_status = data[player_id];
                if (session_status["session_over"] === true) {
                    if (player_id in $buttons) {
                        $buttons[player_id]
                            .addClass("sessionOver")
                            .prop("href", "#pelataan-taas-huomenna");
                    } else {
                        $("a#kokeile")
                            .addClass("sessionOver")
                            .prop("href", "#pelataan-taas-huomenna")
                            .unbind("click");
                    }
                }
            }
        });
    }
}

function addPlayer(map) {
    var players = $.cookie('players');
    
    if (players === null || players === undefined)
        players = [];
    else
        players = $.parseJSON(players);

    // check that id is not added already.
    players.push(map);
    
    $.cookie('players',
             JSON.stringify(players),
             { expires: 365, path: '/' });
}

$(document).ready(function() {

    $._preload.context = false;  // Never use AudioContext on main page.

    startMusic();
    animateTitle();

    addPlayerButtons();

    // Detect unsupported browsers
    if (BrowserDetect.browser === "Explorer"
        && BrowserDetect.version < 10) {
        content = $.modal(
            $('#unsupported-browser').clone().css('display', 'block'), {
                fitViewport: true,
                closeOverlay: false,
                closeSelector: null,
                closeKeyCode: null,
                closeText: ''
        });
    }

    // show current view
    $(window).bind('hashchange', function() {
        var hash = location.hash.toString();
        if (hash.startsWith('#liity')) {
            $('#liity').slideDown(function() { $('#joinData').valid(); });
            $('#olenJoLiittynyt').slideUp();
            $('#mainView').slideUp();
        } else if (hash.startsWith('#olen-jo-liittynyt')) {
            $('#liity').slideUp();
            $('#olenJoLiittynyt').slideDown();
            $('#mainView').slideUp();
        } else {
            $('#liity').slideUp();
            $('#olenJoLiittynyt').slideUp();
            $('#mainView').slideDown();

            if (hash.startsWith('#player=')) {
                hash = hash.substring(1);
                var players = hash.split('&');
                for (var i in players) {
                    var player = players[i].split('player=')[1].split(';');
                    if (player.length == 2)
                        addPlayer({ name: decodeURIComponent(player[0]), id: player[1] });
                }
                location.hash = '';
            }

            addPlayerButtons();
        }
    });

    var handleSubmit = function(event) {
        event.preventDefault();
        if ($("#joinData").valid()) {
            $.post('liity',
                $('#joinData').serialize(),
                function(data) {
                    // Store information to server and create local
                    // data in cookie.
                    addPlayer({
                        'name': $('#joinData input[name="name"]').val(),
                        'id': data.id
                    });

                    location.hash = '';
            });
        }
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
                     { expires: 365, path: '/' });
            window.location.href = global.ctx + '/pelaa';
        } else {
            $.post('kokeile', function(data) {
                addPlayer({
                    'guest': true,
                    'name': '__guest',
                    'id': data.id
                });
                $.cookie('guest_player',
                         data.id,
                         { expires: 365, path: '/' });
                $.cookie('active_player',
                         data.id,
                         { expires: 365, path: '/' });
                window.location.href = global.ctx + '/pelaa';
            });
        }
    });

    $('#activateExistingPlayers').click(function(event){
        event.preventDefault();

        $.post('pelinappulat',
               $('#alreadyJoinedData').serialize(),
               function(data) {
                   location.hash = '';
               });
    });


    // trigger view!
    $(window).trigger('hashchange');
});
