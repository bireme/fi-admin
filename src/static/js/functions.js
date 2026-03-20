function consult_VHL(field_id, source, lang){
    var search_exp = "";
    var search_exp_or = "";
    search_exp = $('#' + field_id).val();

   if (search_exp == '') {
      return;
   }

   search_exp_tokens = search_exp.split(" ");
   if (search_exp_tokens.length > 4){
       for (t = 0; t < (search_exp_tokens.length)/2; t++){
           search_exp_or += " " + search_exp_tokens[t];
       }
   }
   if (search_exp_or != ''){
       search_exp = search_exp + " OR (" + search_exp_or + ")";
   }
   search_exp = search_exp.replace(/[:,.]/g,'');

   var search_vhl_url = "http://pesquisa.bvsalud.org/portal/?lang=" + lang + "&q=" + search_exp + "&filter[db][]=" + source;

   window.open(search_vhl_url);
}
