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
    var form = document.actions;
    form.page.value = param;
    form.submit();
}

function search() {
    var form = document.actions;
    form.s.value = document.search.s.value;
    form.submit();
}
