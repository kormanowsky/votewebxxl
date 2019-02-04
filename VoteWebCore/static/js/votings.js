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
        }
        // data checks
        if(!question_data.text || question_data.type === false || question_data.answers.length < 2){
            // error !
            return false;
        }
        var $qWrap = $('<div class="col-12 col-md-6 col-xl-4"></div>'),
            $qCard = $('<div class="card shadow-sm mt-4"></div>'),
            $qCardBody = $('<div class="card-body"></div>'),
            $qText = $('<h3 class="mb-4"></h3>').text(question_data.text);
        $qCardBody.append($qText);
        $qCard.append($qCardBody);
        $qWrap.append($qCard);
        question_data.answers.forEach(function(answer){
            var $div = $("<div></div>"),
                $input = $('<input type="hidden" name="questions[][answers][]" value="' + answer + '">');
            $div.append($input);
            switch(question_data.type){
                case 0:
                    var $btn = $('<button type="button" class="col btn btn-outline-primary">' + answer + '</button>');
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
            $qCardBody.append($div)
        });
        $(".row#questions").append($qWrap);
        return false;
    },
    clearQuestion: function(){
        return false;
    }
}
