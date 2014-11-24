/*

 Game ending, transition to next game and daily session ending

*/

$(document).ready(function(){
    var $nextGame = $('#nextGame');
    if ($nextGame.attr('href') == global.base_ctx + '/') {
        $nextGame.css('visibility', 'hidden');
    }
    $.preload('hugoism',
              global.base_ctx + '/snd/heippa.[ogg,mp3]');
    $.preload('huomenna',
              global.base_ctx + '/snd/pelataan_taas_huomenna.[ogg,mp3]');
    $('body').one('preloaded', function(){
        if ($('meta[name=last_pass]').attr("content") == 'True' 
            || $('.star').length > 2) {
            $('body').play('hugoism');
        }
        if ($('#nextGame').attr('href') == global.base_ctx + '/') {
            //noinspection JSUnresolvedFunction
            $('body').play('huomenna').promise().done(function(){
                $('#nextGame').css('visibility', 'visible');
            });
        }
    });
});
