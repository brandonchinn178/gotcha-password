$(document).ready(function() {
    $(".label").click(function() {
        $(this).prev("input:radio").prop("checked", true);
    });

    $("button.cancel").click(function() {
        window.location = "/login/";
        return false;
    });

    // validate labels
    $("button.submit").click(function() {
        $(".error").remove();

        var unique = {};
        var empty = $(".image").map(function() {
            var value = $(this).find("input:checked").val();
            if (value === undefined) {
                // no input was selected
                return -1;
            } else {
                unique[value] = true;
            }
        });

        // check if any image has no labels
        if (empty.length > 0) {
            showError(".buttons", "Please select a label for each image.");
            return false;
        }

        // check that no labels are repeated
        if (unique.length !== $(".image").length) {
            showError(".buttons", "Please use each label exactly once.");
            return false;
        }
    });
});

var showError = function(elem, message) {
    $("<p>")
        .addClass("error")
        .text(message)
        .insertAfter(elem);
};
