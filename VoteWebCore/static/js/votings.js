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