function consult_DeCS(field_id, lang){
    var search_exp = "";
    var decs_url = "https://decs.bvsalud.org/" + lang + "/ths?filter=ths_exact_term_bool";

    $('#' + field_id + ' option:selected').each(function() {
        var current_term = $(this).text();

        // remove addiotinal information of term ex. Child (6 to 12 years old)
        if (current_term.includes(' (')){
            current_term = current_term.substring(0, current_term.indexOf('(')-1);
        }

        search_exp += '"' + current_term + '" OR ';
    });

   if (search_exp == "") {
      return;
   }else{
      search_exp = search_exp.substring(0, search_exp.length - 4);

      decs_url +=  "&q=" + search_exp;
   }

   open_window(decs_url);
}


function open_window(url){
    var w = 785;    // window width
    var h = 600;    // window height

    // calculate position to center field assist window
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;

    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;

    new_win = window.open(url, 'fi_admin_win', 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);
    if (window.focus) {
        new_win.focus();
    }

}
