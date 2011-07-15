$(document).ready(function(){
    twttr.anywhere(function (T) {
        T("#follow-placeholder").followButton('startechconf');
    });
    $("#selectlanguage").change(function(){
        newLang = $(this).val();
        if ($(this).attr("current") == newLang)
            return;
        location.href = "/?hl="+newLang;
    });
    
    $('.abstract-link').toggle(
      function (e) {
        e.preventDefault();
        $("#abstract-" + this.id).show();
      }, 
      function (e) {
        e.preventDefault();
        $("#abstract-" + this.id).hide();
      }
    );
});