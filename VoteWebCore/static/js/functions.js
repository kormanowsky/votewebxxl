function CSRF_Token() {
    return $("#global_scrf_token").attr('value');
}

function AjaxForm(element, success, error, autoClose) {
    autoClose = autoClose || false;
    // Для форм в модальных окнах - очищаем форму при закрытии окна
    if ($(element).parents(".modal").length) {
        $(element).parents(".modal").find(".close").click(function () {
            setTimeout(function () {
                ClearForm($(element));
            }, 600);
        });

    }
    element.submit(function (event) {
        event.preventDefault();
        var url = element.attr('action'),
            data = element.serialize();
        $.post(url, data, function (data) {
            if (typeof data === "object") {
                if ('is_valid' in data) {
                    if (data['is_valid'] === false) {
                        for (var key in data['errors']) {
                            ShowMessage("danger", data['errors'][key]);
                        }
                    } else {
                        if (autoClose)
                            $(element).parents(".modal").find(".close").click();
                        ShowMessage("success", "Success!");
                        if (typeof success === "function")
                            success(data);
                    }
                }
            } else {
                if (autoClose)
                    $(element).parents(".modal").find(".close").click();
                if (typeof success === "function")
                    success(data);
            }



        }, error);
    });
}

function ClearForm(element, afterClear) {
    element.find(":input").not('[type="radio"], [type="checkbox"], [type="hidden"]').val("");
    element.find("input[type='radio'], input[type='checkbox']").each(function (i, e) {
        e.checked = false;
    });
    if (typeof afterClear === "function") {
        afterClear();
    }
    return false;
}

function InitMasonry() {
    $(".masonry-wrapper").each(function (i, e) {
        $(e).masonry({
            itemSelector: ".masonry-item"
        })
    });

    $(window).on('resize', LayoutMasonry);
}

function LayoutMasonry() {
    $(".masonry-wrapper").each(function (i, e) {
        $(e).masonry('layout')
    });
}

function AddConfirmationModal(e, text) {
    // Повторно не делаем
    if (parseInt($(e).attr('data-dam-processed'))) {
        return;
    }
    // Устанавливаем тип кнопки там, где его нет
    if (e.nodeName === "BUTTON" && !$(e).attr('type')) {
        $(e).attr('type', 'button');
    }
    // Сброс атрибута onclick
    if (e.onclick) {
        var onclick = e.onclick;
        $(e).click(function (event) {
            onclick.apply(e, event);
        });
        $(e).removeAttr('onclick');
    }
    // Сброс атрибута href 
    if ($(e).attr("href") && $(e).attr("href") != "#") {
        var href = $(e).attr("href");
        $(e).click(function (event) {
            window.location = href;
        });
        $(e).attr('href', '#');
    }
    // Запоминание обработчиков
    var eventListeners = jQuery._data(e, 'events') ? jQuery._data(e, 'events').click : [],
        newEventListeners = [];
    // Создание новых обработчиков
    for (var i in eventListeners) {
        var listener = eventListeners[i];
        if (typeof listener === "object") {
            var handler = listener.handler;
            newEventListeners.push(function (event) {
                handler.apply(e, event);
            });
        }
    }
    // Сброс обработчиков
    $(e).off('click');
    // Установка нового обработчика
    $(e).click(function (event) {
        $('#confirmModalText').text(text);
        var openModalLink = $('<a data-toggle="modal" data-target="#confirmModal"></a>');
        $('body').append(openModalLink);
        openModalLink.click().remove();
        // Проверка, хочет ли пользователь совершить действие
        $('#confirmModalYes').click(function () {
            for (var i in newEventListeners) {
                newEventListeners[i](event);
            }
        });
    });
    // Пометка, что мы уже обработали этот элемент
    $(e).attr('data-dam-processed', 1);
}

function InitConfirmationModal() {
    $(".dangerous-action").each(function (i, e) {
        AddConfirmationModal(e, 'Do you really want to do this?');
    });
}

function TurnOnLeaveConfirmationModal() {
    $("a").not(".dangerous-action").not("[href='#']").each(function (i, e) {
        AddConfirmationModal(e, 'You have unsaved changes. Do you really want to leave this page and lose them?');
    });
}

function InitForm(form){
    form.change(TurnOnLeaveConfirmationModal);
    form.find('input.datepicker, .input-daterange input').on('blur', TurnOnLeaveConfirmationModal);
    form.find('button[type="button"]').on('click', TurnOnLeaveConfirmationModal);
    var MutationObserver = window.MutationObserver;
    if (typeof MutationObserver === "function") {
        var observer = new MutationObserver(function (records) {
            TurnOnLeaveConfirmationModal();
        });
        observer.observe(form[0], {
            childList: true,
            subtree: true
        });
    }
}

function ShowMessage(type, message) {
    var $message = $('<div class="alert alert-' + type + ' alert-dismissible fade show shadow"></div>'),
        $btn = $('<button type="button" class="close" data-dismiss="alert" aria-label="Close"><span aria-hidden="true">&times;</span></button>'),
        $span = $('<span class="d-block mr-5"></span>');
    $span.text(message);
    $message.append($span);
    $message.append($btn);
    $("#messages").append($message);
}

function DefaultAjaxError() {
    message = "An error occured while doing request to server";
    if (arguments.length && arguments[0].statusText != "error") {
        message += ": " + arguments[0].statusText;
    } else {
        message += ".";
    }
    ShowMessage("warning", message);
}