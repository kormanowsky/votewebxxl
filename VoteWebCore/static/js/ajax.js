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

$('#send_report').click(function () {
    $.post('/report', $('#test-report').serialize(), function (data) {
        console.log(data);
        $('#report-error').html('');
        if ('is_valid' in data && 'errors' in data) {
            if (data['is_valid'] === false) {
                var html_msg = '<ul>';
                for (var key in data['errors']) {
                    html_msg += '<li>';
                    html_msg += data['errors'][key] + ': ' + key;
                    html_msg += '</li>';
                }
                html_msg += '</ul>';
                $('#report-error').html(html_msg);
            }
            else
            {
                $('#report-error').html('Success!');
            }
        }
    })
});