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
    // Ajax-формы
    AjaxForm($("#report-form"), false, false, true);
    AjaxForm($("#comment-form"), function (data) {
        if ($("#comments>p").length) {
            $("#comments>p").remove();
        }
        $("#comments").prepend(data.comment);
        $("#comments-count").text(data.comments_count);
    }, false, true);
});