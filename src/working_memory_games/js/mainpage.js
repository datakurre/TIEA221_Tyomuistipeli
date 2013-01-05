// TODO move to library.
if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

function startMusic() {
    $.preload('sudit', 
	      global.ctx + '/snd/Pelit_ja_Pensselit_by_Ahti_Laine.[mp3,ogg]');
    $('body').on('preloaded', function(){
	console.log("ah");
	$('<div></div>').play('sudit');
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
        $(this)
            .delay(idx*100)
            .animate({'top':'-80px'}, 300)
            .animate({'top':'0px'}, 400+idx*50);
    });
}

function addPlayerButtons() {
    
    $('#majorRow .player').remove();

    var players = $.cookie('players');
    if (players == null) return;
    players = $.parseJSON(players).reverse();
    for (idx in players) {
	var btn = $('#buttonTemplate a').clone();
	btn.find('#name').text(players[idx].name);
	btn.attr('player', players[idx].id);
	$("#majorRow .center").prepend(btn);
	btn.show();
	btn.click(function(event){
	    $.cookie('active_player', $(this).attr('player'));
	});
    }
}



$(document).ready(function() {

    startMusic();

    animateTitle();

    addPlayerButtons();
    
    // show current view
    $(window).bind('hashchange', function(){
        var hash = location.hash.toString();
        if (hash.startsWith('#liity')) {
            $('#joinView').slideDown();
            $('#mainView').slideUp();
        } else {
            $('#joinView').slideUp();
            $('#mainView').slideDown();
	    addPlayerButtons();
        }
        $('#join').click(function(event){
            event.preventDefault();

	    $.post('liity',
                $('#joinData').serialize(),
                function(data){
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
                }
              );

        });
    });

    // trigger view!
    $(window).trigger('hashchange');
});
