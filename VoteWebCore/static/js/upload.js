var Upload = window.Upload = {};
Upload.init = function (input, success, error) {
    error = error || DefaultAjaxError;
    var image = false,
        upload_as = input.attr('data-upload-as'),
        csrf_token = input.next().attr('value'), 
        label = $("[for='" + input.attr('id')+"']");
    if (input.attr("data-image-selector")) {
        image = $(input.attr("data-image-selector"));
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
                if(typeof success === "function"){
                    return success(data);
                }
            },
            "error": error,
        });
    });
}