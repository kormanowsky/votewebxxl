function QuizSaveOneClick(task_no, quest_no, answ_text) {
    var request_param = {
        'task_no': task_no,
        'quest_no': quest_no,
        'answ_text': answ_text
    };

    ajaxRequest("GET", 'quiz_save', QuizSaveResponse, request_param);
}

function QuizSaveResponse(data) {
    if (data['ErrorCode'] === 0) {
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

function ajaxRequest(method, url, callback_function, httpParams) {
    var callback_func = callback_function || function (data) {
        console.log('AjaxRequest doesnt have handle function');
    };

    var request = new XMLHttpRequest();
    if (method === "POST") {
        request.open(method, url, false);
        request.send(httpParams);
    }
    else if (method === "GET") {
        request.open(method, url + makeGETParams(httpParams), false);
        request.send();
    }

    if (request.status !== 200) {
        alert('Failed to connection status:' + request.status + ' Response text: ' + request.responseText);
    }
    else {
        callback_func(JSON.parse(request.responseText));
    }
}

function makeGETParams(params) {
    var url = '?';
    for (var key in params) {
        url += key + "=" + params[key] + "&"
    }
    return url;
}