(function(window, $) {
    "use strict";

    function getOption(options, name, defaultValue) {
        if (options && options[name] !== undefined) {
            return options[name];
        }
        return defaultValue;
    }

    function parseMessageData(data) {
        var descriptor = {
            action: "REPLACE",
            text: null,
            code: null,
            type: null,
            ai_model: null,
            ai_suggestion: null
        };

        if (typeof data === "string") {
            var decs_data = data.split("|");
            descriptor.text = decs_data[0];
            descriptor.code = decs_data[1];
            descriptor.action = decs_data[2] || descriptor.action;
            descriptor.type = decs_data[3] || null;
        } else if (typeof data === "object" && data !== null) {
            descriptor.text = data.text;
            descriptor.code = data.code;
            descriptor.action = data.action || descriptor.action;
            descriptor.type = data.type || null;
            descriptor.ai_suggestion = data.ai_suggestion;
            descriptor.ai_model = data.ai_model;
        } else {
            if (window.console && window.console.warn) {
                window.console.warn("Unexpected message data type:", data);
            }
        }

        return descriptor;
    }

    function getDescriptorRowFromField(fieldValue) {
        if (fieldValue === null || fieldValue === undefined) {
            return null;
        }
        return fieldValue.toString().replace(/[A-Za-z_$-]/g, "");
    }

    function findOrCreateDescriptorRow(options) {
        var totalFormsSelector = getOption(options, "totalFormsSelector", "#id_main-descriptor-content_type-object_id-TOTAL_FORMS");
        var descriptorPrefix = getOption(options, "descriptorPrefix", "main-descriptor-content_type-object_id");
        var addButtonSelector = getOption(options, "addButtonSelector", "#descriptors .icon-plus-sign");
        var startAt = getOption(options, "emptyRowStart", 1);
        var totalLines = $(totalFormsSelector).val();

        for (var count = startAt; count < totalLines; count++) {
            var descriptorRow = $("#id_" + descriptorPrefix + "-" + count + "-code");
            if (descriptorRow.val() == "") {
                return count.toString();
            }
        }

        $(addButtonSelector).click();
        return totalLines.toString();
    }

    function setDescriptorRow(row, descriptor, options) {
        var descriptorPrefix = getOption(options, "descriptorPrefix", "main-descriptor-content_type-object_id");
        var supportPrimary = getOption(options, "supportPrimary", true);
        var supportAiMetadata = getOption(options, "supportAiMetadata", true);
        var baseId = descriptorPrefix + "-" + row;

        $("#id_" + baseId + "-code").val(descriptor.code);
        $("#id_" + baseId + "-text").val(descriptor.text);

        if (supportAiMetadata && descriptor.ai_suggestion !== null && descriptor.ai_suggestion !== undefined) {
            $("#id_" + baseId + "-ai_suggestion").val(descriptor.ai_suggestion);
            $("#id_" + baseId + "-ai_model").val(descriptor.ai_model);
        }

        if (supportPrimary && descriptor.type == "PRIMARY") {
            $("#id_" + baseId + "-primary").prop("checked", true);
        }

        $("#label_" + baseId + "-text").html(descriptor.text);
        $("#label_" + baseId + "-text").removeClass("placeholder-style");
    }

    function registerDescriptorReceiver(options) {
        options = options || {};

        var eventMethod = window.addEventListener ? "addEventListener" : "attachEvent";
        var eventer = window[eventMethod];
        var messageEvent = eventMethod == "attachEvent" ? "onmessage" : "message";
        var fieldName = getOption(options, "fieldName", "decs_field");

        eventer(messageEvent, function(e) {
            var descriptor = parseMessageData(e.data);

            if (descriptor.action == "ADD") {
                window[fieldName] = findOrCreateDescriptorRow(options);
            }

            var decsRow = getDescriptorRowFromField(window[fieldName]);
            if (decsRow !== null) {
                setDescriptorRow(decsRow, descriptor, options);
            }
        }, false);
    }

    window.FiAdminDeCSMessages = {
        registerDescriptorReceiver: registerDescriptorReceiver,
        parseMessageData: parseMessageData,
        setDescriptorRow: setDescriptorRow,
        findOrCreateDescriptorRow: findOrCreateDescriptorRow
    };
})(window, jQuery);
