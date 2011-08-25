$(document).ready(function(){
    twttr.anywhere(function (T) {
        T("#follow-placeholder").followButton('startechconf');
    });
    $("#selectlanguage").change(function(){
        newLang = $(this).val();
        if ($(this).attr("current") == newLang)
            return;
        location.href = location.pathname + "?hl="+newLang;
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
    
    // important news block
    var _div = jQuery('#important-new');
    if (_div) {
      _div.animate({
        "opacity": "1"
      }, 1500);
    }    
});