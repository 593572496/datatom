import os
from django.http import HttpResponse
from django.core.cache import cache
import filetype
from django.core.paginator import Paginator
from user.form import UserEmail, UserModifyProfile
from datatom.settings import BASE_DIR
from custom_lib.json_response import render_json
from common import errors
from .logic import send_email_code, decide_user_use_db, new_code_str, new_image_code, get_cookie_value, \
    get_cache_or_update_cache, update_profile_db_and_cache, upload_image_updata_db_and_cache, check_power, \
    query_all_user_db_or_cache, refresh_all_user_in_cache, refresh_user_in_cache
from user.models import User, UserAuthority, Authority, UserData


# 注册获取验证码,点击发送验证码后调用该接口（post传回参数:user_name(email)）
def get_vcode(request):
    form = UserEmail(request.POST)
    if form.is_valid():
        send_email_code(form.cleaned_data.get('user_name'))
        return render_json(None)
    else:
        return render_json(form.errors, errors.EMAIL_FORMAT_ERROR)


def check_vcode(request):
    email = request.POST.get('user_name')
    vcode = request.POST.get('vcode')
    email_key = '-'.join([email, 'vcode'])
    cache_vcode = cache.get(email_key)
    if cache_vcode:
        if vcode == cache_vcode:
            return render_json(None)
        else:
            return render_json(None, errors.VCODE_ERROR)

    else:
        return render_json(None, errors.EMAIL_ERROR)


def register(request):
    user_name = request.POST.get('user_name')
    user_password = request.POST.get('user_password')  # 采用md5加密，md5的固定长度为32位
    user_db = decide_user_use_db(user_name)  # 用户应该使用的db
    if len(user_password) == 32:
        user_object, created = User.objects.using(user_db).get_or_create(user_name=user_name,
                                                                         user_password=user_password)
        if created:
            user_object.profile(user_db)  # 创建用户时初始化个人资料
            user_object.have_all_authority(user_db)  # 初始化个人权限
            return render_json(None)
        else:
            return render_json(None, errors.USER_IS_EXIST)
    else:
        return render_json(None, errors.PASSWORD_FORMAT_ERROR)


def login_code(request):  # 输入用户和密码后点击登录，获取验证码，只验证user_name格式是否符合要求，如符合要求则返回验证码，不符合返回user_name格式错误
    form = UserEmail(request.POST)
    if form.is_valid():
        new_code = new_code_str()
        cache_key = '-'.join([form.cleaned_data.get('user_name'), 'logincode'])
        cache.set(cache_key, new_code, 120)  # 缓存验证码字符串2分钟
        return HttpResponse(content=new_image_code(new_code), content_type='image/png')
    else:
        return render_json(None, errors.USER_NAME_FORMAT_ERROR)


def login(request):  # 输入验证码后，点击确认后，开始确认登录
    user_name = request.POST.get('user_name')
    user_password = request.POST.get('user_password')
    user_code = request.POST.get('code')
    code_cache_key = '-'.join([user_name, 'logincode'])
    user_db = decide_user_use_db(user_name)
    if str(user_code.lower()) == str(cache.get(code_cache_key)).lower():  # 验证码不区分大小写,str避免验证码为空时.lower报错
        if User.objects.using(user_db).filter(user_name=user_name,
                                              user_password=user_password).exists():
            user_object = User.objects.using(user_db).get(user_name=user_name)
            user_cache_key = '-'.join([user_name, 'user-cache-key'])
            user_object.have_all_authority(user_db)  # 手动执行将用户详情信息绑定到user对象上
            user_object.profile(user_db)  # 手动执行将用户权限信息绑定到user对象上
            cache.set(user_cache_key, user_object, 86400)  # 缓存个人信息86400秒，一天
            request.session['user_name'] = user_name
            request.session.set_expiry(0)  # 关闭浏览器时session清空
            cookie_cache_key = '-'.join([user_name, 'cookie_key'])
            cookie_value = get_cookie_value()
            cache.set(cookie_cache_key, cookie_value, 1800)  # 缓存cookie信息1800秒，半个小时,缓存的key为username+cookie_key
            response = render_json(None)
            response.set_cookie(key='cookie_key', value=cookie_value)  # 默认设置时客户端浏览器关闭时客户端的cookie失效
            return response
        else:
            return render_json(None, errors.USER_OR_PASSWORD_ERROR)
    else:
        return render_json(None, errors.USER_CODE_ERROR)


# 以下接口都是登录过后的接口，需要验证cookie,另外用户相关信息每次都优先从缓存中获取，缓存中不存在则需要从数据库获取，并重新写入缓存，修改用户信息，则必须重新写入缓存

def user_image(request):  # 用户头像
    image_path = get_cache_or_update_cache(request.session['user_name']).user_profile.user_image
    with open(image_path, 'rb') as f:
        image = f.read()
    return HttpResponse(image, content_type='image/png')


def user_profile(request):  # 获取用户资料
    user = get_cache_or_update_cache(request.session['user_name'])
    data = {
        'account number': user.user_name,
        'user_nickname': user.user_profile.user_nickname,
        'user_sex': user.user_profile.sex,
        'user_power': user.user_authority_list
    }
    return render_json(data)


def user_modify_profile(request):  # 用户修改资料,并更新缓存
    form = UserModifyProfile(request.POST)
    if form.is_valid():
        new_profile = form.cleaned_data
        update_profile_db_and_cache(request.session['user_name'], new_profile)
        return render_json(None)
    else:
        return render_json(form.errors, errors.POST_USER_PROFILE_ERROR)


def user_modify_image(request):  # 用户修改头像，也需更新内存
    new_image = request.FILES.get('new_image')
    if new_image:
        kind = filetype.guess(new_image)
        if kind.extension in ['png', 'jpg', 'jpeg']:
            if new_image.size > 5242660:  # 图片大小不能超过5M
                return render_json(None, errors.UPLOAD_IMAGE_SIZE_IS_TOOBIG)
            else:
                image_path = os.path.join(BASE_DIR, r'media\image', request.session['user_name'])
                with open(image_path, 'wb') as f:
                    for chunk in new_image.chunks():
                        f.write(chunk)
                    f.flush()  # 将数据刷到硬盘上
                upload_image_updata_db_and_cache(request.session['user_name'], image_path)  # 更新数据库和缓存
                return render_json(None)
        else:
            return render_json(None, errors.UPLOAD_IMAGE_TYPE_IS_ERROR)

    else:
        return render_json(None, errors.UPLOAD_IMAGE_IS_NULL)


# 刷新个人信息
def refresh_user(request):
    refresh_user_in_cache(request.session.get('user_name'))
    return render_json(None)


def logout(request):
    user_name = request.session.get('user_name')
    # >>>>>>> 清理session不生效？
    #  清理session
    # del request.session['user_name']
    # >>>>>>>>>>>
    # 清理cache中cookie
    cookie_cache_key = '-'.join([user_name, 'cookie_key'])
    cache.delete(cookie_cache_key)
    # 清理浏览器的cookie
    response = render_json(None)
    response.delete_cookie('cookie_key')
    return response


def change_password(request):  # 修改密码
    user_name = request.session.get('user_name')
    user_use_db = decide_user_use_db(user_name)
    new_password = request.POST.get('new_password')
    old_password = request.POST.get('old_password')
    if User.objects.using(user_use_db).filter(user_name=user_name, user_password=old_password).exists():
        User.objects.using(user_use_db).filter(user_name=user_name).update(user_password=new_password)
        return render_json(None)
    else:
        return render_json(None, errors.CHECK_OLD_PASSWORD_FAILED)


# 以下接口需要验证用户的权限，上传补丁，删除补丁，编辑补丁，修改用户权限（超级管理员拥有所有的权限，管理员拥有补丁上传、修改权限，普通用户只有浏览的权限）,一个用户只有一种权限
# 列出所有的用户及权限（只有SuperAdmin才能调用这个接口）
# 考虑一个问题如果数据已经缓存到了内存中，此时有新用户增加，就不能就是更新到缓存中，所以应该增加一个刷新按钮，刷新缓存，
@check_power('SuperAdmin')  # 查询所有的用户
def query_all_user(request):
    page_number = request.GET.get('page_number', 1)
    user_list = query_all_user_db_or_cache()
    p = Paginator(user_list, 5)
    page = p.page(page_number)
    page_user_list = [user.user_name for user in page.object_list]
    data = {
        'user_count': p.count,
        'page_count': p.num_pages,
        'page_user_data': page_user_list,
        'page_has_next': page.has_next(),
        'page_has_previous': page.has_previous(),

    }
    return render_json(data)


# 刷新缓存中的所有用户
@check_power('SuperAdmin')
def refresh_all_user_cache(request):
    refresh_all_user_in_cache()
    return render_json(None)


# SuperAdmin 给用户增加权限,只有SuperAdmin采用这个权限，SuperAdmin无法修改和删除自己的权限
# 是否需要刷新缓存中user_all信息，(使用刷新按钮)，是否需要刷新个人的信息（使用刷新按钮）
# 因为使用的cache_key是固定的格式，所以可尝试先从cache中查找，查找不到再从数据库中获取(管理员的操作，是否有必要？)
# 一个用户只能有一种权限，所以增加权限的时候，需要删除之前的权限
@check_power('SuperAdmin')  # 增加用户的权限
def add_power_on_user(request):
    power = request.POST.get('power')
    add_power_user_name = request.POST.get('add_power_user_name')
    if request.session['user_name'] == add_power_user_name:  # SuperAdmin无法修改自己的权限，但是可以修改另外一个SuperAdmin的权限
        return render_json(None, errors.DONT_MODIFY_SELF_POWER)
    if power in ['SuperAdmin', 'Admin']:
        add_power_user_use_db = decide_user_use_db(add_power_user_name)
        # add_power_user_id = get_cache_or_update_cache(add_power_user_name).id
        add_power_user_id = User.objects.using(add_power_user_use_db).filter(user_name=add_power_user_name).first().id
        UserAuthority.objects.using(add_power_user_use_db).filter(user_id=add_power_user_id).delete()  # 清除之前的权限（需要优化）
        power_id = Authority.objects.using(add_power_user_use_db).filter(power=power).first().id
        UserAuthority.user_add_authority(add_power_user_id, power_id, add_power_user_use_db)
        return render_json(None)
    else:
        return render_json(None, errors.SET_POWER_ERROR)


@check_power('SuperAdmin')  # 删除用户的权限
def remove_power_on_user(request):
    power = request.POST.get('power')
    remove_power_user_name = request.POST.get('remove_power_user_name')
    if request.session['user_name'] == remove_power_user_name:  # SuperAdmin无法修改自己的权限，但是可以修改另外一个SuperAdmin的权限
        return render_json(None, errors.DONT_MODIFY_SELF_POWER)
    if power in ['SuperAdmin', 'Admin']:
        remove_power_user_use_db = decide_user_use_db(remove_power_user_name)
        # remove_power_user_id = get_cache_or_update_cache(remove_power_user_name).id
        remove_power_user_id = User.objects.using(remove_power_user_use_db).filter(
            user_name=remove_power_user_name).first().id
        power_id = Authority.objects.using(remove_power_user_use_db).filter(power=power).first().id
        UserAuthority.user_remove_authority(remove_power_user_id, power_id, remove_power_user_use_db)
        return render_json(None)
    else:
        return render_json(None, errors.SET_POWER_ERROR)


@check_power('SuperAdmin')  # 查询单个用户
def query_user(request):
    query_user_name = request.GET.get("query_user_name")
    user_use_db = decide_user_use_db(query_user_name)
    user = User.objects.using(user_use_db).filter(user_name=query_user_name).first()
    if user:
        user_data = {
            'user_nickname': user.profile(user_use_db).user_nickname,
            'user_sex': user.profile(user_use_db).sex,
            'user_power': user.have_all_authority(user_use_db)
        }
        return render_json(user_data)
    else:
        return render_json(None, errors.QUERY_USER_DONT_EXIST)


@check_power('SuperAdmin')  # 删除用户
def remove_user(request):
    remove_user_name = request.GET.get('remove_user_name')
    if remove_user_name == request.session.get('user_name'):  # 防止误删除自己
        return render_json(None, errors.DONT_REMOVE_SELF)
    user_use_db = decide_user_use_db(remove_user_name)
    user = User.objects.using(user_use_db).filter(user_name=remove_user_name).first()
    if user:
        UserData.objects.using(user_use_db).filter(id=user.id).first().delete()
        UserAuthority.objects.using(user_use_db).filter(id=user.id).all().delete()
        user.delete()
        return render_json(None)
    else:
        return render_json(None, errors.REMOVE_USER_DONT_EXIST)


@check_power('SuperAdmin')  # 重置密码
def reset_user_password(request):
    reset_user_name = request.GET.get('reset_user_name')
    reset_user = User.objects.using(decide_user_use_db(reset_user_name)).filter(user_name=reset_user_name).first()
    if reset_user:
        reset_user.user_password = 'e10adc3949ba59abbe56e057f20f883e'  # 重置成123456
        reset_user.save()
        return render_json(None)
    else:
        return render_json(None, errors.REST_PASSWORD_USER_DONT_EXIST)
