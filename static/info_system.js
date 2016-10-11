$(function() {

  setInterval(function(){
    $.get("/info_system", function(data) {
      $("#info_system").html(data);
    });
  }, 1000);
  
  
});
