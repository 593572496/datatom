from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache
from custom_lib.json_response import render_json
from common import errors
from user.logic import get_cookie_value

"""用户登录后cookie验证中间件"""
"""不需要验证的接口"""
WHITE_LIST = [
    '/user/register/',
    '/user/sendvcode/',
    '/user/checkvcode/',
    '/user/logincode/',
    '/user/login/'
]


class CookieMiddleware(MiddlewareMixin):
    def process_request(self, request):  # 判断访问的路由是否是白名单里面的，如果是白名单里面的直接返回空，结束循环
        for url in WHITE_LIST:
            if request.path.startswith(url):
                return
        # 以下是对非白名单的处理
        cookie_value = request.COOKIES.get('cookie_key')
        if not cookie_value:
            return render_json(None, errors.USER_COOKIE_ERROR)  # cookie错误跳转至登录界面
        user_name = request.session.get('user_name')
        if not user_name:  # 判断session是否正常有数据，无数据的话直接跳转至登录界面
            return render_json(None, errors.USER_SESSION_ERROR)
        cookie_cache_key = '-'.join([user_name, 'cookie_key'])
        if cookie_value == cache.get(cookie_cache_key):
            return
        else:
            return render_json(None, errors.USER_COOKIE_ERROR)  # cookie错误跳转至登录界面

    def process_response(self, request, response):
        for url in WHITE_LIST:
            if request.path.startswith(url):
                return response
        # 每次返回时更新cookie的ttl 半个小时页面无操作，需要重新登录
        user_name = str(request.session.get('user_name'))
        cookie_cache_key = '-'.join([user_name, 'cookie_key'])
        cache.touch(cookie_cache_key, 1800)
        return response

    """
    每次返回都更新cookie，是否能实现
    cookie_value = get_cookie_value()
    cache.set(cookie_cache_key, cookie_value, 1800)  # 缓存cookie信息半小时,缓存的key为username+cookie_key
    response.set_cookie(key='cookie_key', value=cookie_value)
    """
