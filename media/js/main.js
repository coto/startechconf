$(document).ready(function(){
	var id = "#msg";

	function show(id) {
		
		//Get the screen height and width
		var maskHeight = $(document).height();
		var maskWidth = $(window).width();
		//Get the window height and width
		var winH = $(window).height();
		var winW = $(window).width();
		console.log(winH  + " - " + winW);
		console.log($(id).height());
		console.log( winH/2-$(id).height()/2);

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
	
	$("#action-open-register").click(function(e){
		//Cancel the link behavior
		e.preventDefault();
		id = "#register";
		show(id);
	});
	
	//if close button is clicked
	$('.action-close-register').click(function (e) {
		//Cancel the link behavior
		e.preventDefault();

		$('#mask').hide();
		$(id).hide();
		location.href="/";
	});		

	//if mask is clicked
	$('#mask').click(function () {
		$(this).hide();
		$(id).hide();
	});
	
	id = "#msg";
	if ($(id).size()) show(id);
	
});