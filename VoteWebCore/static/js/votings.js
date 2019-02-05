var Votings = window.Votings = {};
Votings.setCurrentButtonAnswer = function(element){
    var $element = $(element),
        answer = $element.text().trim(),
        question_id = $element.attr('data-question-id'),
        $input = $("input[name='answer_" + question_id + "']");
    $input.attr('value', answer);
    $element.siblings("button.btn-primary").toggleClass("btn-outline-primary btn-primary");
    $element.toggleClass("btn-outline-primary btn-primary");
    return false;
}
Votings.checkVotingForm = function(){
    var $form = $('form');
}
Votings.creation = {
    addPossibleAnswerInput: function(element){
        var $element = $(element),
            $divInputGroup = $('<div class="input-group mt-2"></div>'),
            $input = $('<input class="input-possible-answer form-control">'),
            $divInputGroupAppend = $('<div class="input-group-append"></div>'),
            $inputRemoveBtn = $('<button class="btn btn-outline-danger"></button>'),
            $inputRemoveIcon = $('<i class="la la-times"></i>');
        $inputRemoveBtn.append($inputRemoveIcon).attr('onclick', 'return Votings.creation.removePossibleAnswerInput(this);');
        $divInputGroupAppend.append($inputRemoveBtn);
        $divInputGroup.append($input);
        $divInputGroup.append($divInputGroupAppend);
        $divInputGroup.insertBefore($element);
        return false;
    },
    removePossibleAnswerInput: function(element){
        var $element = $(element);
        $element.parent().parent().remove();
        return false;
    },
    addQuestion: function(element){
        var question_data = {
            "text": (function(){
                var text = $("#input-text").val().trim();
                if(text.length){
                    return text;
                }
                return false;
            })(),
            "type": (function(){
                var type = false;
                $("input.input-question-type").each(function(index, input){
                    if(typeof type === "number"){
                        return;
                    }
                    if(input.checked){
                        type = parseInt(input.value);
                    }
                });
                return type;
            })(),
            "answers": (function(){
                var answers = [];
                $("#form-group-answers input").each(function(index, input){
                    var $input = $(input),
                        answer = $input.val().trim();
                    if(answer.length){
                        answers.push(answer)
                    }
                });
                return answers;
            })(),
        };
        // data checks
        if(!question_data.text || question_data.type === false || question_data.answers.length < 2){
            // error !
            return false;
        }
        if(question_data.type === 0 && question_data.answers.length > 3 || question_data.type === 2 && question_data.answers.length < 3){
            question_data.type = 1;
        }
        var qId = $('#questions .card').length ? +$($('#questions .card')[$('#questions .card').length-1]).attr("data-q-id")+1 : 0, 
            $qWrap = $('<div class="col-12 col-md-6 col-xl-4"></div>'),
            $qCard = $('<div class="card shadow-sm mt-4"></div>'),
            $qCardBody = $('<div class="card-body"></div>'),
            $qText = $('<h3 class="mb-4"></h3>').text(question_data.text), 
            $qTextInput = $('<input type="hidden" name="questions[' + qId + '][text]" value="' + question_data.text + '">'), 
            $qTypeInput = $('<input type="hidden" name="questions[' + qId + '][type]" value="' + question_data.type + '">'), 
            $qRemoveLink = $('<a href="#" onclick="return Votings.creation.removeQuestion(this);" class="text-danger"></a>');
        $qCardBody.append($qTextInput);
        $qCardBody.append($qTypeInput);
        $qCardBody.append($qText);
        $qCard.append($qCardBody);
        $qCard.attr("data-q-id", qId);
        $qWrap.append($qCard);
        question_data.answers.forEach(function(answer){
            var $div = $("<div></div>"),
                $input = $('<input type="hidden" name="questions[' + qId + '][answers][]" value="' + answer + '">');
            $div.append($input);
            switch(question_data.type){
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
            $qCardBody.append($qRemoveLink);
            
        });
        if($("#no-questions").length){
            $("#no-questions").remove();
        }
        $(".row#questions").append($qWrap);
        Votings.creation.clearQuestion();
        $("#addQuestionModal .close").click();
        return false;
    },
    clearQuestion: function(){
        window.ClearForm($("#addQuestionModal"), function(){
            $("#form-group-answers").html('<label for="input-text">Possible answers</label><div class="input-group"><input type="text" class="input-possible-answer form-control" placeholder="Yes"><div class="input-group-append"><button onclick="return Votings.creation.removePossibleAnswerInput(this);" class="btn btn-outline-danger" value=""><i class="la la-times"></i></button></div></div><div class="input-group mt-2"><input type="text" class="input-possible-answer form-control" placeholder="No"><div class="input-group-append"><button onclick="return Votings.creation.removePossibleAnswerInput(this);" class="btn btn-outline-danger" value=""><i class="la la-times"></i></button></div><button onclick="return Votings.creation.addPossibleAnswerInput(this);" class="btn btn-outline-primary mt-2 w-100">Add possible answer</button>');
        });
        return false;
    }, 
    removeQuestion: function(element){
        $(element).parent().parent().parent().remove();
    }, 
    checkForm: function(element){
        var $element = $(element);
        if($element.find("#questions .card").length == 0){
            return false;
        }
    }
}
