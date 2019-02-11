var Upload = window.Upload = {};
Upload.init = function (input, success, error) {
    error = error || DefaultAjaxError;
    var image = false,
        id_input = false,
        upload_as = input.attr('data-upload-as'),
        csrf_token = CSRF_Token(),
        label = $("[for='" + input.attr('id')+"']");
    if (input.attr("data-image-selector")) {
        image = $(input.attr("data-image-selector"));
        if(!parseInt(image.attr('data-no-helper'))){
            var p = $('<p class="text-center">No image</p>');
            p.insertBefore(image);
            image.on('load', function(){
                p.addClass('d-none');
                return false;
            });
            image.on('error', function(){
                p.removeClass('d-none');
                return false;
            });
        }
    }
    if (input.attr("data-input-id-selector")) {
        id_input = $(input.attr("data-input-id-selector"));
    }
    input.on('change', function () {
        var file = input[0].files[0],
            data = new FormData();
        data.append("file", file);
        data.append("csrfmiddlewaretoken", csrf_token);
        if(label.length){
            label.text(file.name);
        }
        $.ajax({
            "url": "/api/upload/" + upload_as,
            "method": "POST",
            "data": data,
            "contentType": false,
            "processData": false,
            "success": function(data){
                if(!("id" in data)){
                    if(typeof error === "function"){
                        return error(data);
                    }
                }
                if(image){
                    image.attr('src', data.data.url);
                }
                if(id_input){
                    id_input.attr('value', data.id);
                }
                if(typeof success === "function"){
                    return success(data);
                }
            },
            "error": error,
        });
    });
}