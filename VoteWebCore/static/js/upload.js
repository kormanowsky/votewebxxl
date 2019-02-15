var Upload = window.Upload = {};
Upload.init = function (input, success, error) {
    error = error || DefaultAjaxError;
    var image = false,
        id_input = false,
        remove_link = false,
        upload_as = input.attr('data-upload-as'),
        csrf_token = CSRF_Token(),
        label = $("[for='" + input.attr('id') + "']"),
        _success = function (data) {
                if (!("id" in data)) {
                    if (typeof error === "function") {
                        return error(data);
                    }
                }
                if(remove_link){
                    if(data.id){
                        remove_link.show();
                    }else{
                        remove_link.hide();
                    }
                }
                if (image) {
                    image.attr('src', data.url);
                }
                if (id_input) {
                    id_input.attr('value', data.id);
                }
                if (typeof success === "function") {
                    return success(data);
                }
            }
    if (input.attr("data-image-selector")) {
        image = $(input.attr("data-image-selector"));
        if (parseInt(image.attr('data-no-helper'))) {
            var p = $('<p class="text-center">No image</p>');
            p.insertBefore(image);
            image.on('load', function () {
                p.addClass('d-none');
                return false;
            });
            image.on('error', function () {
                p.removeClass('d-none');
                return false;
            });
        }
    }
    if (input.attr("data-input-id-selector")) {
        id_input = $(input.attr("data-input-id-selector"));
    }
    if (input.attr("data-remove-selector")) {
        remove_link = $(input.attr("data-remove-selector"));
        remove_link.click(function(event){
            $.ajax({
            "type": "POST",
            "url": "/api/upload/" + upload_as,
            "data": {'csrfmiddlewaretoken': CSRF_Token(), 'file': false},
            "success": _success,
            "error": error,
        })
        return false;
        })
    }
    input.on('change', function () {
        var file = input[0].files[0],
            data = new FormData();
        data.append("file", file);
        data.append("csrfmiddlewaretoken", csrf_token);
        if (typeof file === "object" && label.length) {
            label.text(file.name);
        }
        $.ajax({
            "url": "/api/upload/" + upload_as,
            "method": "POST",
            "data": data,
            "contentType": false,
            "processData": false,
            "success": _success,
            "error": error,
        });
    });
}