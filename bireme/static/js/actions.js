$(function(){

    var form = document.actions;

    if(form != null) {

        var orderby = form.orderby.value;
        var order = form.order.value;

        if(orderby != "" && order != "") {
            var obj = $("#id_" + orderby);
            if(order === "-") {
                obj.html(obj.html() + " <i class='icon-caret-up'></i>");
            } else {
                obj.html(obj.html() + " <i class='icon-caret-down'></i>");
            }
        }
    }

    $( "#show_advaced_filters" ).click(function() {
      $( ".advanced_filters" ).toggle();
      return false;
    });

});

function orderby(param) {
    var form = document.actions;

    if(form.orderby.value == param) {
        if(form.order.value == "-") {
            form.order.value = "+";
        } else {
            form.order.value = "-";
        }
    } else {
        form.orderby.value = param;
        form.order.value = "+";
    }
    form.submit();
}

function page(param) {
    var form = document.search;
    form.page.value = param;
    form.submit();
}

function search() {
    var form = document.actions;
    form.s.value = document.search.s.value;
    form.submit();
}

function filter_owner(owner) {
    var form = document.actions;
    form.filter_owner.value = owner;
    form.page.value = 1;
    form.submit();
}

function change_type(type) {
    var form = document.actions;
    form.type.value = type;
    form.page.value = 1;
    form.submit();
}
