$(document).ready(function() {

    $('#msg').maxlength({
		events: [], // Array of events to be triggerd
		maxCharacters: 125, // Characters limit
		status: true, // True to show status indicator bewlow the element
		statusClass: "status", // The class on the status div
		statusText: "caracteres restantes", // The status text
		notificationClass: "notification",  // Will be added when maxlength is reached
		showAlert: false, // True to show a regular alert message
		alertText: "You have typed too many characters.", // Text in alert message
		slider: false // True Use counter slider
	});

});

