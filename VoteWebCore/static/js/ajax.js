function AjaxForm(element, success, error){
    element.submit(function(event){
        event.preventDefault();
        var url = element.attr('action'),
            data = element.serialize();
        // TODO: check if request is successful in JSON
        $.post(url, data, success, error);
    });
}

function ClearForm(element, afterClear){
    element.find(":input").not('[type="radio"], [type="checkbox"], [type="hidden"]').val("");
    element.find("input[type='radio'], input[type='checkbox']").each(function(i, e){
        e.checked = false;
    });
    if(typeof afterClear === "function"){
        afterClear();
    }
    return false;
}

function QuizSaveOneClick(task_no, quest_no, answ_text) {
    var request_param = {
        'task_no': task_no,
        'quest_no': quest_no,
        'answ_text': answ_text
    };
    return $.ajax({
        url: "/quiz_save",
        method: "GET",
        data: request_param,
        success: QuizSaveResponse,
    });
}

function QuizSaveResponse(data) {

    if (data['ErrorCode'] === 0) {
        $('#Button_ID_' + data['ButtonID'] + '_NO').parent().toggleClass("d-flex d-none");
        $('#complete_txt_' + data['ButtonID']).toggleClass("d-none d-block");
        document.getElementById('complete_txt_' + data['ButtonID']).style.visibility = "visible";
    }
    else if (data['ErrorCode'] === 2) {
        var complete_txt = document.getElementById('complete_txt_' + data['ButtonID']);
        if (complete_txt) {
            complete_txt.style.color = "#ff0000";
            complete_txt.innerText = "Already done";
            complete_txt.style.visibility = "visible";
        }
    }
    document.getElementById('quest_form_' + data['ButtonID']).style.visibility = "hidden";
}

function makeGETParams(params) {
    var url = '?';
    for (var key in params) {
        url += key + "=" + params[key] + "&"
    }
    return url;
}

jQuery(function($){
    $('#report-form-errors').hide();
    AjaxForm($("#report-form"), function(data){
        $("#report-form-errors").html('');
        if ('is_valid' in data && 'errors' in data) {
            if (data['is_valid'] === false) {
                var errors_list = $('ul');
                for (var key in data['errors']) {
                    var error_li = $('li');
                    error_li.text(data['errors'][key] + ': ' + key);
                    errors_list.append(error_li);
                }
                $('#report-form-errors').addClass('text-danger').append(errors_list).show();
            }else{
                $('#report-form').hide();
                $('#report-form-errors').addClass('text-success').html('Success!').show();
                $('#reportModal .close').click(function(){
                    setTimeout(function(){
                        $('#report-form-errors').hide();
                        $('#report-form').show();
                        ClearForm($("#report-form"));
                    }, 600);
                });
            }
        }
    });
});