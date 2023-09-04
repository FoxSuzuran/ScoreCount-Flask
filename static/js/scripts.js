$(document).ready(function () {
    // 自动刷新页面，定时刷新每10秒钟
    setInterval(function () {
        location.reload();
    }, 3000);

    // 点击按钮触发计算操作
    $('#calculate-button').click(function () {
        // 发送请求给后端进行计算
        $.ajax({
            url: '/calculate',
            type: 'POST',
            success: function (response) {
                $('#calculation-result').text(response.message);
            },
            error: function () {
                $('#calculation-result').text('计算失败，请重试。');
            }
        });
    });
});
