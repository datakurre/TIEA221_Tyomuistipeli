// TODO move to library.
if (typeof String.prototype.startsWith != 'function') {
  String.prototype.startsWith = function (str){
    return this.slice(0, str.length) == str;
  };
}

$(document).ready(function() {

    // Animate title
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

    // load player buttons
    $.get($('meta[name=context]').attr("content")
          + "/list_players", function(data) {
        $("#majorRow .center").prepend(data);
    });

    // show current view
    $(window).bind('hashchange', function(){
        var hash = location.hash.toString();
        if (hash.startsWith('#liity')) {
            $('#joinView').slideDown();
            $('#mainView').slideUp();
        } else {
            $('#joinView').slideUp();
            $('#mainView').slideDown();
        }
        $('#join').click(function(event){
            event.preventDefault();
            // post data, create player id to cookie based on json
            // object returned for the req.
        });
    });

    // trigger view!
    $(window).trigger('hashchange');
});
