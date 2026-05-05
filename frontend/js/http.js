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
},
//    login: function(obj){
//      $.ajax({
//        url: baseApiUrl + '/user/login',
//        type: 'POST',
//        data: {
//          username: obj.username,
//          password: obj.password
//        },
//        success: function(res) {
//          console.log('success'); //sy-log
//          console.log(res); //sy-log
//
//          // if(res.code === 1){
//          //   console.log('登录成功'); //sy-log
//          //   localStorage.setItem('username', res.data)
//            layer.msg('登录成功，即将跳转~', function () {
//              location.href = 'index'
//            });
//          // }else {
//          //   layer.msg(res.msg, function () {});
//          // }
//        }
//      })
//
//    },
    getMenu: function() {
      var that = this;
      if (!$('#side-nav').length) {
        return;
      }
      $.ajax({
        url: baseApiUrl + '/user/menu',
        type: 'POST',
        data: {
          username: localStorage.getItem('username'),
        },
        success: function(res) {
          if(res.code === 1){
            var menuList = res.data.menu;
            var items = [];
            var _ul = $('<ul></ul>').addClass('nav').attr('id', 'nav');
            $.each(menuList, function(index, val) {
              var icon = val.icon ? '<i class="layui-icon layui-icon-'+ val.icon +'"></i>': '<i class="layui-icon layui-icon-app"></i>';
              var item = '<li id="menu' + val.id + '"><a _href="' + val.url + '">'+ icon +'<cite>' + val.name +
                '</cite><i class="iconfont nav_right">&#xe697;</i></a></li>';

              items.push(item);
              if (val.children && val.children.length) {
                //有二级子菜单
                setTimeout(function() {
                  that.getSubMenu(val.id, val.children);
                }, 500);
              }
            });
            $('#side-nav').empty();
            _ul.append(items.join(''));
            $('#side-nav').append(_ul);
          }else {
            layer.msg(res.msg, function () {});
          }
        }
      })
    },
    /**
     * @param {Object} id 上级子菜单id,拼接menu获取元素
     * @param {Object} subList 子菜单列表
     */
    getSubMenu: function(id, subList) {
      var that = this;
      var subItems = [];
      var subUl = $('<ul></ul>').addClass('sub-menu');
      $.each(subList, function(idx, sub) {
        var subItem = '<li id="menu' + sub.id + '"><a _href="' + sub.url + '"><i class="iconfont">&#xe6a7;</i><cite>' +
          sub.name + '</cite></a></li>';
        subItems.push(subItem);
        if (sub.children && sub.children.length) {
          setTimeout(function() {
            that.getSubMenu(sub.id, sub.children);
          }, 1500);
        }
      });
      subUl.append(subItems.join(''));
      $('#menu' + id).append(subUl);
    }
  }
	exports('http', request);

});
