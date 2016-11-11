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

        var empty = $(".image").map(function() {
            if ($(this).find("input:checked").length === 0) {
                return false;
            }
        });

        if (empty.length > 0) {
            showError(".buttons", "Please select a label for each image.");
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
