var Votings = window.Votings = {};
Votings.setCurrentButtonAnswer = function (element) {
    var $element = $(element),
        answer = $element.text().trim(),
        question_id = $element.attr('data-question-id'),
        $input = $("input[name='answer_" + question_id + "']");
    $input.attr('value', answer);
    $element.siblings("button.btn-primary").toggleClass("btn-outline-primary btn-primary");
    $element.toggleClass("btn-outline-primary btn-primary");
    return false;
}
Votings.checkVotingForm = function () {
    var $form = $('form');
    // TODO: write this
}
Votings.getQuestion = function(id, success){
    return $.ajax({
        "url": "/api/get-question/" + id,
        "method": "GET", 
        "success": success
    });
}
Votings.edit = {
    clearPossibleAnswers: function(){
        $('#form-group-answers').html('');
    },
    addPossibleAnswerInput: function (answer) {
        answer = answer || "";
        var $divInputGroup = $('<div class="input-group mt-2"></div>'),
            $input = $('<input class="input-possible-answer form-control" value="' + answer + '">'),
            $divInputGroupAppend = $('<div class="input-group-append"></div>'),
            $inputRemoveBtn = $('<button class="btn btn-outline-danger"></button>'),
            $inputRemoveIcon = $('<i class="la la-times"></i>');
        $inputRemoveBtn.append($inputRemoveIcon).attr('onclick', 'return Votings.edit.removePossibleAnswerInput(this);');
        $divInputGroupAppend.append($inputRemoveBtn);
        $divInputGroup.append($input);
        $divInputGroup.append($divInputGroupAppend);
        $('#form-group-answers').append($divInputGroup);
        return false;
    },
    removePossibleAnswerInput: function (element) {
        var $element = $(element);
        $element.parent().parent().remove();
        return false;
    },
    openQuestionModal: function(question_id){
        question_id = question_id || 0;
        var $a = $('<a data-toggle="modal" data-target="#questionModal"></a>');
        $('body').append($a);
        $a.click();
        $a.remove();
        $("#questionModal").attr("data-question-id", question_id);
        if(question_id){
            Votings.getQuestion(question_id, function(question){
                $("#questionModalLabel").text("Edit question #" + question.id);
                $("#input-text").val(question.text);
                $("#input-question_type_" + question.type).click();
                Votings.edit.clearPossibleAnswers();
                for(var answer_index in question.answers){
                    var answer = question.answers[answer_index];
                    Votings.edit.addPossibleAnswerInput(answer);
                }
            });
        }else{
            $("#questionModalLabel").text("Add question");
        }
        return false;
    }, 
    closeQuestionModal: function(){
        $("#questionModal .close").click();
    },
    saveQuestion: function (element) {
        var question_data = {
            "csrfmiddlewaretoken": $("#question-form input[name='csrfmiddlewaretoken']").attr("value"),
            "question_id": parseInt($("#questionModal").attr('data-question-id')),
            "text": (function () {
                var text = $("#input-text").val().trim();
                if (text.length) {
                    return text;
                }
                return false;
            })(),
            "type": (function () {
                var type = false;
                $("input.input-question-type").each(function (index, input) {
                    if (typeof type === "number") {
                        return;
                    }
                    if (input.checked) {
                        type = parseInt(input.value);
                    }
                });
                return type;
            })(),
            "answers": (function () {
                var answers = [];
                $("#form-group-answers input").each(function (index, input) {
                    var $input = $(input),
                        answer = $input.val().trim();
                    if (answer.length) {
                        answers.push(answer)
                    }
                });
                return answers;
            })(),
        };
        // data checks
        if (!question_data.text || question_data.type === false || question_data.answers.length < 2) {
            return false;
        }
        if (question_data.type === 0 && question_data.answers.length > 3 || question_data.type === 2 && question_data.answers.length < 3) {
            question_data.type = 1;
        }
        $.ajax({
            "url": "/api/save-question",
            "data": question_data,
            "method": "POST",
            "success": function (question_data) {
                var qId = question_data.id,
                    $qWrap = $('<div class="col-12 col-md-6 col-xl-4"></div>'),
                    $qCard = $('<div class="card shadow-sm mt-4"></div>'),
                    $qCardBody = $('<div class="card-body"></div>'),
                    $qText = $('<h3 class="mb-4"></h3>').text(question_data.text),
                    $qIdInput = $('<input type="hidden" name="questions[]" value="' + qId + '">'),
                    $qEditLink = $('<a href="#" onclick="return Votings.edit.openQuestionModal(' + qId + ');" class="mr-4"></a>'),
                    $qRemoveLink = $('<a href="#" onclick="return Votings.edit.removeQuestion(this);" class="text-danger"></a>');
                $qCardBody.append($qIdInput);
                $qCardBody.append($qText);
                $qCard.append($qCardBody);
                $qCard.attr("data-q-id", qId);
                $qWrap.append($qCard);
                question_data.answers.forEach(function (answer) {
                    var $div = $("<div></div>");
                    switch (question_data.type) {
                        case 0:
                            var $btn = $('<button type="button" class="col btn btn-outline-primary mb-3">' + answer + '</button>');
                            $div.append($btn);
                            break;
                        case 1:
                            var $divControl = $('<div class="custom-control custom-radio mb-3"></div>'),
                                $label = $('<label class="custom-control-label">' + answer + '</label>');
                            $divControl.append($label);
                            $div.append($divControl);
                            break;
                        case 2:
                            var $divControl = $('<div class="custom-control custom-checkbox mb-3"></div>'),
                                $label = $('<label class="custom-control-label">' + answer + '</label>');
                            $divControl.append($label);
                            $div.append($divControl);
                            break;
                    }
                    $qCardBody.append($div);
                    $qRemoveLink.text('Remove question');
                    $qEditLink.text('Edit');
                    $qCardBody.append($qEditLink);
                    $qCardBody.append($qRemoveLink);

                });
                if ($("#no-questions").length) {
                    $("#no-questions").remove();
                }
                if($(".row#questions div[data-q-id='" + question_data.id + "']").length){
                    $(".row#questions div[data-q-id='" + question_data.id + "']").parent().remove();
                }
                $(".row#questions").append($qWrap);
                Votings.edit.clearQuestion();
                Votings.edit.closeQuestionModal();
                return false;
            }
        });
    },
    clearQuestion: function () {
        window.ClearForm($("#question-form"), function () {
            Votings.edit.clearPossibleAnswers();
            Votings.edit.addPossibleAnswerInput("Yes");
            Votings.edit.addPossibleAnswerInput("No");
        });
        return false;
    },
    removeQuestion: function (element) {
        $(element).parent().parent().parent().remove();
        if($("#questions").children().length == 0){
            $("#questions").html('<div id="no-questions" class="col-12"><h5 class="p-5 text-center">Click Add to add a question</h5></div>');
        }
    },
    checkForm: function (element) {
        var $element = $(element);
        if ($element.find("#questions .card").length == 0) {
            return false;
        }
    }
}