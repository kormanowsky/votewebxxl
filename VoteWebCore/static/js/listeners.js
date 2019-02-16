jQuery(function ($) {
    // Установка ширины содержимого в 375px для тех экранов, которые меньше 375px
    var width = $(window).width();
    if (width < 375) {
        var viewportTag = $('meta[name="viewport"]');
        viewportTag.attr('content', viewportTag.attr('content').replace('device-width, initial-scale=1.0', '375'));
    }
    // Загрузка картинок
    $(".upload-image").each(function (index, input) {
        window.Upload.init($(input));
    });
    // Запрет на закрытие моального окна кнопками
    $('.modal').attr('data-keyboard', 'false').attr('data-backdrop', 'static');
    // Улучшенная обработка изменеия формы
    $("form").each(function (i, form) {
        InitForm($(form));
    });
    // Опасные действия
    $(".modal").last().css("z-index", "1059");
    InitConfirmationModal();
    // Инициализация карточек
    InitMasonry();
    // Обрабатываем ссылки и/или перерисовываем карточки при изменении DOM
    var MutationObserver = window.MutationObserver;
    if (typeof MutationObserver === "function") {
        var observer = new MutationObserver(function (records) {
            InitConfirmationModal();
            records.forEach(function (record) {
                if (record.addedNodes.length && $(record.target).hasClass('masonry-wrapper')) {
                    $(record.target).masonry('addItems', record.addedNodes);
                } else if (record.removedNodes.length && $(record.target).hasClass('masonry-wrapper')) {
                    $(record.target).masonry('remove', record.removedNodes);
                }
                LayoutMasonry();
            });
        });
        observer.observe(document.body, {
            attributes: true,
            childList: true,
            subtree: true
        });
    }
    // Выбор даты
    $('.input-daterange').datepicker();
    var timepickerConfig = {
            useCurrent: true,
            icons: {
                time: 'la la-time',
                date: 'la la-calendar',
                up: 'la la-arrow-up',
                down: 'la la-arrow-down',
                previous: 'la la-arrow-left',
                next: 'la la-arrow-right',
                today: 'la la-screenshot',
                clear: 'la la-trash',
                close: 'la la-remove'
            },
        },
        timepickerChecker = function (date) {
            if (date.getTime() < Date.now()) {
                $('#input-datetime_closed_time').data('DateTimePicker').minDate(new Date);
            } else {
                $('#input-datetime_closed_time').data('DateTimePicker').minDate(false);
            }
        };
    $('#input-datetime_closed_time').datetimepicker(timepickerConfig);
    initialDate = $('#input-datetime_closed_date').datepicker('getDate');
    if (initialDate) {
        timepickerChecker(initialDate);
    }
    $('#input-datetime_closed_date').datepicker().on('changeDate', function (event) {
        timepickerChecker(event.date);
    });
    // Ajax-формы
    AjaxForm($("#report-form"), false, false, true);
    AjaxForm($("#comment-form"), function (data) {
        if ($("#comments>p").length) {
            $("#comments>p").remove();
        }
        $("#comments").prepend(data.comment);
        $("#comments-count").text(data.comments_count);
    }, false, true);
    // Картинки на главной
    $('.img_data').click(function () {
        $('#big_img').attr('src', this.currentSrc);
        var temp_link = $('<a id="Test3213" href="#" data-toggle="modal" data-target="#modal-big-img"></a>');
        temp_link.appendTo('body');
        temp_link.trigger('click');
        temp_link.remove();
    });
});