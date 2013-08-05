
$(document).ready(function(){
    if ($('#nextGame').attr('href') == global.base_ctx + '/') {
        $('#nextGame').style('visibility', 'hidden');
    }
    $.preload('hugoism',
              global.base_ctx + '/snd/hugoismit/hugoismi'+(Math.floor(Math.random()*19))+'.[ogg,mp3]');
    $.preload('huomenna',
              global.base_ctx + '/snd/pelataan_taas_huomenna.[ogg,mp3]');
    $.preload('lopuke',
              global.base_ctx + '/snd/lopuke.[ogg,mp3]');
    $('body').one('preloaded', function(){
        if ($('meta[name=last_pass]').attr("content") == 'True' 
            || $('.star').length > 2) {
            $('body').play('hugoism');
        }
        if ($('#nextGame').attr('href') == global.base_ctx + '/') {
            $('body').play('huomenna').promise().done(function(){
                $('#nextGame').style('visibility', 'visible');
                $('body').play('lopuke');
            });
        }
    });
});
