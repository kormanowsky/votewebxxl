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