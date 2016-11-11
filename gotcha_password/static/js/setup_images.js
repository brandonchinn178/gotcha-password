$(document).ready(function() {
    $("button.cancel").click(function() {
        window.location = "/create-account/";
        return false;
    });

    // validate labels
    $("button.submit").click(function() {
        $(".error").remove();

        var errors = $(".image input").map(function() {
            var text = $(this).val();
            if (text.trim() === "") {
                showError(this, "Label is empty.");
                return false;
            }
            if (text.length > 255) {
                showError(this, "Label is longer than 255 characters.");
                return false;
            }
        });

        if (errors.length > 0) {
            showError(".buttons", "Please provide valid labels.");
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
