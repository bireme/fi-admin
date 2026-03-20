// function responsible for formatting attribute labels in JSON display
function format_attrlabel(value) {
    if ( value != 'text'){
        label = value.replace('_','')
        return  label + ':'
    }else{
        return ''
    }
}

// function responsible for display JSON elements using jsrender template
function display_json_value(element){
    var element_id = $(element).attr('id');
    var element_val = $('#' + element_id).val();

    var json_data = jQuery.parseJSON(element_val);

    if ( json_data != null ){
        $('#' + element_id + '_display').html($("#itensTemplate").render(json_data, {format: format_attrlabel}));
    }
}

$(function() {
    // change default delimiters of jsrender (if jsrender is loaded)
    if (typeof $.views !== 'undefined') {
        $.views.settings.delimiters("[[","]]");
    }

    // render JSON fields for display
    $(".jsonfield").each(function() {
        var field_value = $(this).val();

        // check if hidden value starts with [ or { (JSON object)
        if ( field_value.match(/^[\[|\{]/) ) {
            display_json_value( $(this) );
        }
    });

    // watch for change of hidden fields (JSON elements)
    $(".jsonfield").bind("change", function() {
        display_json_value( $(this) );
    });
});

