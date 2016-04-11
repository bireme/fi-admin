function open_window_with_post(verb, url, data, target) {
    var form = document.createElement("form");
    form.setAttribute("method", verb);
    form.setAttribute("action", url);
    form.setAttribute("target", target);

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
    assist_win = window.open('about:blank', target, 'scrollbars=1,width=785,height=590');

    form.submit();
    if (window.focus) {
        assist_win.focus();
    }
}

function field_assist(field_name){

    field_assist_url = '/bibliographic/field_assist/' + field_name + '/',
    field_value = $('#id_' + field_name).val();

    post_params = {'field_value' : field_value };

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

function update_field_from_assist(field_name, json_string) {

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
    $('#id_' + field_name).val(field_new_value).trigger('change');

    // close field assist window
    assist_win.close();
}
