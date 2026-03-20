$(function() {
    $(document).on("click", "a.delete_confirm", function(){ deleteConfirmation(this); });
    //$(document).on("click", "button.delete", function(){ deleteUser(this); });
});


function deleteConfirmation(element) {  
    $("#delete_confirm_modal").modal("show");
    $("#delete_confirm_modal input#delete_id").val($(element).attr('id'));
}
