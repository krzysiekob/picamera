/*
var eventOutputContainer = document.getElementById("message");
var evtSrc = new EventSource("/subscribe");

evtSrc.onmessage = function(e) {
  console.log(e.data);
  eventOutputContainer.innerHTML = eventOutputContainer.innerHTML + "" + e.data;
};
*/


$(function() {
    
    var evtSrc = new EventSource("/subscribe");
    evtSrc.onmessage = function(e) {
	// console.log(e.data);
	$('#message').show("fast");
	$("#message").append(e.data+"<br>");
	var pos = $('#message').prop('scrollHeight');
	$('#message').scrollTop(pos);

    };
    
    $('.stream').click(function() {
	
	id = $(this).attr("data-id");
	sh = $(this).attr("data-sh");
	data = {"id": id, 'sh': sh};
	error = 0;
	if (sh == 'yt' && id == 'start') {
	    yt_id = $('#YouTube_stream_id').val();
	    console.log(yt_id);
	    if (!yt_id) {
		$('#YouTube_stream_id').addClass('has-error');
		error = 1;
	    }
	    yt_url = $('#YouTube_stream_url').val();
	    console.log(yt_url);
	    if (!yt_url) {
		$('#YouTube_stream_url').addClass('has-error');
		error = 1;
	    }   
	    data['yt_id'] = yt_url+'/'+yt_id;
	}
	console.log(data);
	
	if (error === 0) {
	    $.ajax({
		url: '/publish',
		data: data,
		type: 'POST',
		success: function(response) {
		    console.log(response);
		},
		error: function(error) {
		    console.log(error);
		}
	    });
	}
	
    });

 
    
});
