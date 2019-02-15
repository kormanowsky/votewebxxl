var Votings = window.Votings = {};
Votings.getQuestion = function (id, success) {
    return $.ajax({
        "url": "/api/get-question/" + id,
        "method": "GET",
        "success": success,
        "error": DefaultAjaxError,
    });
}
Votings.vote = {
    setCurrentButtonAnswer: function (element) {
        var $element = $(element),
            answer = $element.text().trim(),
            question_id = $element.attr('data-question-id'),
            $input = $("input[name='answer_" + question_id + "']");
        $input.attr('value', answer);
        $element.siblings("button.btn-primary").toggleClass("btn-outline-primary btn-primary");
        $element.toggleClass("btn-outline-primary btn-primary");
        return false;
    },
    checkForm: function (element) {
        var input_names = [],
            result = true;
        $(element).find('input').each(function (i, input) {
            var $input = $(input);
            if (!(input_names.indexOf($input.attr('name')) + 1)) {
                input_names.push($input.attr('name'));
            }
        });
        input_names.forEach(function (name) {
            var $inputs = $(element).find('[name="' + name + '"]'),
                _result = false;
            $inputs.each(function (i, input) {
                if (input.type == "checkbox" || input.type == "radio") {
                    if (input.checked) {
                        _result = true;
                    }
                } else {
                    if (input.value.length) {
                        _result = true;
                    }
                }
            });
            result = result && _result;
        });
        if (!result) {
            ShowMessage("danger", "You have not voted in all questions. Check your votes and try again.");
        }
        return result;
    }
}
Votings.stats = {
    init: function (id, type, stats) {
        var $canvas = $('#question-' + id + '-stats'),
            canvas = $canvas[0];
        canvas.width = $canvas.parent().width();
        canvas.height = parseInt(canvas.width * 0.75);
        var labels = [],
            data = [],
            colors = [
                '255, 99, 132',
                '54, 162, 235',
                '255, 206, 86',
                '75, 192, 192',
                '153, 102, 255',
                '255, 159, 64',
            ],
            background = [],
            border = [],
            random = function (a, b) {
                if (a > b) {
                    var t = a;
                    a = b;
                    b = t;
                }
                return parseInt(Math.random() * (b - a) + a);
            },
            randomColor = function () {
                var color = [];
                for (var i = 0; i < 3; ++i) {
                    color.push(random(0, 255));
                }
                return color;
            },
            type = type == 2 ? 'bar' : 'pie',
            options = type == 2 ? {
                scales: {
                    yAxes: [{
                        ticks: {
                            beginAtZero: true
                        }
                        }]
                }
            } : {};
        if (labels.length > 6) {
            for (var i = 6; i < labels.length; ++i) {
                colors.push(randomColor.join(', '));
            }
        }
        for (var i = 0; i < colors.length; ++i) {
            background.push('rgba(' + colors[i] + ', 1)');
            border.push('rgba(' + colors[i] + ', 0)');
        }
        for (var label in stats) {
            labels.push(label);
            data.push(stats[label]);
        }
        var chart = new Chart(canvas.getContext('2d'), {
            type: type,
            data: {
                labels: labels,
                datasets: [{
                    label: 'Votes',
                    data: data,
                    backgroundColor: background,
                    borderColor: border,
                    borderWidth: 1
                }]
            },
            options: options,
        });
    }
}
Votings.edit = {
    clearPossibleAnswers: function () {
        $('#form-group-answers').html('');
    },
    addPossibleAnswerInput: function (answer) {
        answer = answer || "";
        var $divInputGroup = $('<div class="input-group col-12 col-md-6 mt-2"></div>'),
            $input = $('<input class="input-possible-answer form-control" value="' + answer + '">'),
            $divInputGroupAppend = $('<div class="input-group-append"></div>'),
            $inputRemoveBtn = $('<button class="btn btn-outline-danger dangerous-action"></button>'),
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
    openQuestionModal: function (question_id) {
        question_id = question_id || 0;
        var $a = $('<a data-toggle="modal" data-target="#questionModal"></a>');
        $('body').append($a);
        $a.click();
        $a.remove();
        $("#questionModal").attr("data-question-id", question_id);
        if (question_id) {
            Votings.getQuestion(question_id, function (question) {
                $("#questionModalLabel").text("Edit question #" + question.id);
                $("#questionModal .close").hide();
                $("#input-text").val(question.text);
                $("#input-question_type_" + question.type).click();
                Votings.edit.clearPossibleAnswers();
                for (var answer_index in question.answers) {
                    var answer = question.answers[answer_index];
                    Votings.edit.addPossibleAnswerInput(answer);
                }
                if (question.image) {
                    $("#question-image").attr('src', question.image.data.url);
                    $("#question-image-id-input").attr('value', question.image.id);
                }else{
                    $("#remove-current-image").addClass('d-none');
                }
            });
        } else {
            $("#questionModalLabel").text("Add question");
            $("#questionModal .close").show();
            $("#remove-current-image").addClass('d-none');
        }
        return false;
    },
    closeQuestionModal: function () {
        $("#questionModal .close").click();
    },
    saveQuestion: function (element) {
        var question_data = {
            "csrfmiddlewaretoken": CSRF_Token(),
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
            "image_id": (function () {
                var image_id = 0,
                    id_input_value = parseInt($("#question-image-id-input").attr('value'));
                if (!isNaN(id_input_value)) {
                    image_id = id_input_value
                }
                return image_id;
            })(),
        };
        // data checks
        if (!question_data.text || question_data.type === false || question_data.answers.length < 2) {
            ShowMessage("danger", "You have not filled all fields or have added less than 2 possible answers. Check the form and try again.");
            return false;
        }
        $.ajax({
            "url": "/api/save-question",
            "data": question_data,
            "method": "POST",
            "success": function (question) {
                $question = $(question.html);
                if ($("#no-questions").length) {
                    $("#no-questions").remove();
                }
                if ($(".row#questions div[data-q-id='" + question.id + "']").length) {
                    $(".row#questions div[data-q-id='" + question.id + "']").parent().remove();
                }
                $(".row#questions").append($question);
                Votings.edit.clearQuestion();
                Votings.edit.closeQuestionModal();
                return false;
            },
            "error": DefaultAjaxError,
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
        $(element).parent().parent().parent().parent().remove();
        if ($("#questions").children().length == 0) {
            $("#questions").html('<div id="no-questions" class="col-12"><h5 class="p-5 text-center">Click Add to add a question</h5></div>');
        }
    },
    checkForm: function (element) {
        var $element = $(element);
        if ($element.find("#questions .card").length == 0) {
            ShowMessage("danger", "You have not added any questions. Add at least one question and try again.");
            return false;
        }
    }
}
Votings.favourites = {
    add: function (element, id) {
        $.ajax({
            "url": "/api/favourites/add/" + id,
            "type": "POST",
            "data": {
                "csrfmiddlewaretoken": CSRF_Token()
            },
            "success": function (data) {
                if (typeof data === "string") {
                    $(element).find("p").text(data);
                    var onclick = $(element).attr("onclick");
                    $(element).attr("onclick", onclick.replace("add", "remove"));
                    $(element).toggleClass("text-light text-primary");
                } else {
                    DefaultAjaxError();
                }
            },
            "error": DefaultAjaxError,
        });
    },
    remove: function (element, id) {
        $.ajax({
            "url": "/api/favourites/remove/" + id,
            "type": "POST",
            "data": {
                "csrfmiddlewaretoken": CSRF_Token()
            },
            "success": function (data) {
                if (typeof data === "string") {
                    $(element).find("p").text(data);
                    var onclick = $(element).attr("onclick");
                    $(element).attr("onclick", onclick.replace("remove", "add"));
                    $(element).toggleClass("text-light text-primary");
                } else {
                    DefaultAjaxError();
                }
            },
            "error": DefaultAjaxError,
        });
    }
}