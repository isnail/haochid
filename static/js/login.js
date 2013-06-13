function loginDialog(url){
    var html = '';
    html += '<form id="login_form">';
    html += '<div>';
    html += '<label for="id_username">帐号:</label>';
    html += '<input type="text" required="required" placeholder="请输入您的帐号" name="username" maxlength="254" id="id_username">';
    html += '<div style="clear: both"></div>';
    html += '</div>';
    html += '<div>';
    html += '<label for="id_password">密码:</label>';
    html += '<input type="password" required="required" placeholder="请输入您的密码" name="password" id="id_password">';
    html += '<div style="clear: both"></div>';
    html += '</div>';
    html += '</form>';
    html += '<button class="image-button bg-color-blue fg-color-white" onclick="login(\''+url+'\')">';
    html += '登录';
    html += '<i class="icon-enter"></i>';
    html += '</button>';
    html += '<br>';
    html += '<button class="image-button bg-color-green fg-color-white" onclick="window.open(\'https://api.weibo.com/oauth2/authorize?client_id=421659899&response_type=code&redirect_uri=http://haochid.com/callback/s\');">';
    html += '新浪微博';
    html += '<img src="/static/images/sina.png">';
    html += '</button>';
    html += '<button class="image-button bg-color-red fg-color-white" onclick="window.open(\'https://open.t.qq.com/cgi-bin/oauth2/authorize?client_id=801167659&response_type=code&redirect_uri=http://haochid.com/callback/t\')">';
    html += '腾讯微博';
    html += '<img src="/static/images/tencent.png">';
    html += '</button>';
    html += '<button class="bg-color-greenDark fg-color-white" onclick="window.open(\'/register\')">';
    html += '注册';
    html += '</button>';

    $.Dialog({
        title: '登录',
        closeButton : true,
        content: html,
        buttons: {}
    });
    $("#dialogButtons").remove();
}
function login(url){
    var errorHtml = '';
    errorHtml += '<div class="notices" id="login_error">';
    errorHtml += '<div class="bg-color-red">';
    errorHtml += '<a class="close" href="javascript:;" onclick="$(this).parent().parent().remove();"></a>';
    errorHtml += '<div class="notice-icon"><img src="/static/images/shield-user.png"></div>';
    errorHtml += '<div class="notice-image"><img src="/static/images/armor.png"></div>';
    errorHtml += '<div class="notice-header fg-color-yellow">登录失败</div>';
    errorHtml += '<div class="notice-text">';
    errorHtml += '请检查您的帐号和密码！';
    errorHtml += '<br>';
    errorHtml += '请妥善保管好您的重要信息。';
    errorHtml += '</div>';
    errorHtml += '</div>';
    errorHtml += '</div>';
    $.post(url, {username: $("#id_username").val(), password: $("#id_password").val()}, function(result){
        if(result.status == 1){
            $("#dialogOverlay").remove();
        }else{
            if($("#login_error").length == 0){
                $("#login_form").append(errorHtml);
            }

        }
    });
}