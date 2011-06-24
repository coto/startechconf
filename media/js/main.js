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
});