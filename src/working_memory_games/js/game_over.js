
$(document).ready(function(){
    $.preload('hugoism',
              global.base_ctx + '/snd/hugoismit/hugoismi'+(Math.floor(Math.random()*19))+'.[ogg,mp3]');
    $.preload('lopuke',
              global.base_ctx + '/snd/lopuke.[ogg,mp3]');
    $('body').one('preloaded', function(){
        $('body').play('hugoism');
        if ($('#nextGame').attr('href') == global.base_ctx + '/')
            $('body').play('lopuke');
    });
});
