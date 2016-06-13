// control display of fields item_form (110), type_of_computer_file (111), type_of_cartographic_material (112)
// type_of_journal (113) and type_of_visual_material (114), specific_designation_of_the_material (115)
$( "#id_record_type" ).change(function() {
    record_type = $("#id_record_type option:selected").val();
    show_hide_field_list(['item_form', 'type_of_computer_file', 'type_of_cartographic_material',
                          'type_of_journal', 'type_of_visual_material', 'specific_designation_of_the_material'], 'hide');

    switch(record_type){
        case "a":
            show_hide_field('item_form', 'show');
            if (literature_type[0] == "S" && treatment_level == "as"){
                show_hide_field('type_of_journal', 'show');
            }else{
                clear_select_option(['type_of_journal', 'type_of_cartographic_material',
                                     'type_of_visual_material', 'specific_designation_of_the_material']);
            }
            break;
        case "c":
        case "d":
        case "i":
        case "j":
        case "p":
        case "t":
            show_hide_field('item_form', 'show');
            clear_select_option(['type_of_computer_file', 'type_of_cartographic_material',
                                 'type_of_journal', 'type_of_visual_material', 'specific_designation_of_the_material']);
            break;
        case "f":
        case "e":
            show_hide_field('item_form', 'show');
            show_hide_field('type_of_cartographic_material', 'show');
            clear_select_option(['type_of_computer_file', 'type_of_journal',
                                 'type_of_visual_material', 'specific_designation_of_the_material']);
            break;
        case "g":
        case "o":
        case "r":
            show_hide_field('item_form', 'show');
            show_hide_field('type_of_visual_material', 'show');
            break;
        case "k":
            show_hide_field('item_form', 'show');
            show_hide_field('type_of_visual_material', 'show');
            show_hide_field('specific_designation_of_the_material', 'show');
            clear_select_option(['type_of_computer_file', 'type_of_cartographic_material', 'type_of_journal']);
            break;
        case "m":
            show_hide_field('type_of_computer_file', 'show');
            clear_select_option(['item_form', 'type_of_cartographic_material', 'type_of_journal',
                                 'type_of_visual_material', 'specific_designation_of_the_material']);
            break;
    }
});

function show_hide_field(fieldname, show_hide){
    if (show_hide == 'show'){
        $("label[for=id_" + fieldname + "], #id_" + fieldname + "").show();
    }else{
        $("label[for=id_" + fieldname + "], #id_" + fieldname + "").hide();
    }
}
function show_hide_field_list(fieldlist, show_hide){
    for (i=0; i< fieldlist.length; i++) {
        show_hide_field(fieldlist[i], show_hide);
    }
}

function clear_select_option(fieldlist){
    for (i=0; i< fieldlist.length; i++) {
        $("#id_" + fieldlist[i] + "").val("");
    }

}
