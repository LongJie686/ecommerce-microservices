/*
 * @Author: https://github.com/WangEn
 * @Author: https://gitee.com/lovetime/
 * @Date:   2020-07-29
 * @lastModify 2020-07-30 16:45:40
 * +----------------------------------------------------------------------
 * | Weadmin [ 后台管理模板 ]
 * | 基于Layui http://www.layui.com/
 * +----------------------------------------------------------------------
 */
layui.define(['jquery', 'layer'], function(exports) {
  var $ = layui.jquery,
    layer = layui.layer;

  var baseApiUrl = window.location.origin;

  var request = {
    hello: function(str){
      alert('Hello '+ (str||'mymod'));
    },
login: function(obj){
  $.ajax({
    url: baseApiUrl + '/api/users/login',
    type: 'POST',
    contentType: 'application/json',
    data: JSON.stringify({
      username: obj.username,
      password: obj.password
    }),
    success: function(res) {
      if(res.code === 200 && res.data && res.data.token){
        localStorage.setItem('login', JSON.stringify(1));
        localStorage.setItem('username', obj.username);
        localStorage.setItem('token', res.data.token);
        localStorage.setItem('user_id', res.data.user.id);
        layer.msg('登录成功', function () {
          location.href = 'index_new.html'
        });
      } else {
        localStorage.setItem('login', JSON.stringify(0));
        layer.msg(res.message || '登录失败');
      }
    },
    error: function(xhr) {
      layer.msg('登录失败，请检查用户名和密码');
    }
  })
}
  }
	exports('http', request);

});
