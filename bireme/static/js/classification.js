function open_popup_win(url, target) {
    var w = 615;    // field assist window weight
    var h = 600;    // field assist window height

    // calculate position to center field assist window
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;

    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;

    popup_win = window.open(url, target, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

    if (window.focus) {
        popup_win.focus();
    }
}

function open_classification(c_type, object){
    classification_url = '/classification/classify/' + c_type + '/' + object + '/';

    open_popup_win(classification_url, 'classification');
    return false;
}

function get_json_text_by_language(field_name, language){
    field = $('#id_' + field_name).val();
    field_text = '';
    console.log(field);
    if (field != null && field != ''){
        field_json = jQuery.parseJSON(field);

        var count;
        for (count = 0; count < field_json.length; count++ ){
            if (field_json[count]['_i'] == lang){
                field_text = field_json[count]['text'];
            }
        }
    }
    return field_text;

}

function open_decs_suggestions(language){
    lang = language.substring(0,2);
    if (lang == 'en'){
        field_title = $('#id_english_translated_title').val();
    }else{
        field_title = get_json_text_by_language('title', lang);
    }
    field_abstract = get_json_text_by_language('abstract', lang);

    field_value = field_title + ' ' + field_abstract;

    decs_suggestion_url = '/utils/decs_suggestion/';
    post_params = {'field_value' : field_value};

    open_window_with_post('POST', decs_suggestion_url, post_params, 'decs_suggestions');
    return false;
}
