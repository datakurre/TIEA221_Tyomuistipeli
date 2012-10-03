


$(document).ready(function(){

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

    // bind buttons
    $('#join').click(function(event){
	$(this).slideUp();
    });

});