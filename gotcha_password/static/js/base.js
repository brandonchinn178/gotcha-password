$(document).ready(function() {
    // cancel buttons by default go to the home page
    $("button.cancel").click(function() {
        window.location = "/";
        return false;
    });
});
