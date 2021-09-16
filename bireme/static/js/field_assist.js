function open_window_with_post(verb, url, data, target) {
    var form = document.createElement("form");
    form.setAttribute("method", verb);
    form.setAttribute("action", url);
    form.setAttribute("target", target);

    var w = 785;    // field assist window weight
    var h = 600;    // field assist window height

    // calculate position to center field assist window
    var dualScreenLeft = window.screenLeft != undefined ? window.screenLeft : screen.left;
    var dualScreenTop = window.screenTop != undefined ? window.screenTop : screen.top;

    var width = window.innerWidth ? window.innerWidth : document.documentElement.clientWidth ? document.documentElement.clientWidth : screen.width;
    var height = window.innerHeight ? window.innerHeight : document.documentElement.clientHeight ? document.documentElement.clientHeight : screen.height;

    var left = ((width / 2) - (w / 2)) + dualScreenLeft;
    var top = ((height / 2) - (h / 2)) + dualScreenTop;


    if (data) {
        for (var key in data) {
            var input = document.createElement('input');
            input.type = 'hidden';
            input.name = key;
            input.value = typeof data[key] === "object" ? JSON.stringify(data[key]) : data[key];
            form.appendChild(input);
        }
    }
    document.body.appendChild(form);
    assist_win = window.open('about:blank', target, 'scrollbars=yes, width=' + w + ', height=' + h + ', top=' + top + ', left=' + left);

    form.submit();
    if (window.focus) {
        assist_win.focus();
    }
}

function field_assist(field_name, field_id, module_name){
    // set default args values
    field_id = typeof field_id !== 'undefined' ? field_id : field_name;
    module_name = typeof module_name !== 'undefined' ? module_name : 'biblioref';

    field_assist_url = '/utils/field_assist/' + field_name + '/',
    field_value = $('#id_' + field_id).val();
    if (field_value == 'null' || field_value == null){
        field_value = '';
    }

    post_params = {'field_value' : field_value, 'field_id': field_id, 'module_name': module_name};

    open_window_with_post('POST', field_assist_url, post_params, 'field_assist');
    return false;
}

function escape_linebreaks(str) {
    return str
      .replace(/[\n]/g, '\\n')
      .replace(/[\r]/g, '\\r')
      .replace(/[\t]/g, '\\t')
    ;
}

function update_field_from_assist(field_name, json_string, field_id) {

    var json_string_esc = escape_linebreaks(json_string);
    // convert to json_string to json object
    try{
        json_obj = jQuery.parseJSON(json_string_esc);
    }catch (err){
        alert(err);
    }
    // select content of data element (just used for wrap de objects)
    json_data = json_obj['data'];

    // convert json to string for save at database
    field_new_value = JSON.stringify(json_data);

    // update field with string json and trigger change function
    $('#id_' + field_id).val(field_new_value).trigger('change');

    // close field assist window
    assist_win.close();
}
