$(document).ready(function(){
    twttr.anywhere(function (T) {
        T("#follow-placeholder").followButton('startechconf');
    });

	function show(id) {
		//Get the screen height and width
		var maskHeight = $(document).height();
		var maskWidth = $(window).width();
		//Get the window height and width
		var winH = $(window).height();
		var winW = $(window).width();

		//Set heigth and width to mask to fill up the whole screen
		$('#mask').css({'width':maskWidth,'height':maskHeight});
		
		//transition effect		
		$('#mask').fadeTo("slow",0.8);

		//Set the popup window to center
		$(id).css('top',  winH/2-$(".modal-border").height()/2);
		$(id).css('left', (winW/2-$(".modal-border").width()/2)-120);

		//transition effect
		$(id).fadeIn(100);
	}
    var id = "#msg";

	$("#action-open").click(function(e){
		e.preventDefault();
        id = $(this).attr("rel");
        show(id);
	});
	
	$('.action-close').click(function (e) {
		e.preventDefault();

		$('#mask').hide();
		$($(this).attr("rel")).hide();
	});		

	$('#mask').click(function () {
		$(this).hide();
		$(id).hide();
	});
	
	if ($(id).size()) show(id);

});