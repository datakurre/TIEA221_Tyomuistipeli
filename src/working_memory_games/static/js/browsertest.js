
var global = global || {}
global.userid = 0;
global.ctx = $('meta[name=context]').attr("content");

$(document).ready(function(){
    var html5versions = { 
	'mozilla': '3.5',
	'msie': '3.5',
	'opera': '12.0'
    };
    var version = parseFloat($.browser.version)
    console.log(version);
    console.log($.browser);
    if ($.browser.webkit
	|| ($.browser.opera && version >= 12.)
	|| ($.browser.mozilla && version >= 9.0)
	|| ($.browser.msie && version >= 3.5)) {
	// pass happily

	startSession();

    } else {
	alert("Työmuistipeli on toteutettu selaimella pelattavaksi, mutta tarvitset uudemman selaimen pelataksesi.");
	window.location = "http://www.mozilla.org/fi/firefox/"
    }

});

function startSession() {
    console.log("start")

    var id = $.cookie("client.id");
    console.log(id);
    if (id === undefined || id == null)
	$.get(global.ctx + '/rest/new/client', 
	      function(data) {
		  $.cookie("client.id", data);
		  id = data;
	      });

    $(document.body).append($('<button >Luo uusi käyttäjä</button>'));

}