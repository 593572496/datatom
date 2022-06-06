import os
import random
from io import BytesIO
from uuid import uuid4
from django.core.mail import send_mail
from random import randint
from django.core.cache import cache
from celery_worker import call_by_worker
from hashlib import md5
from PIL import Image, ImageFont, ImageDraw
from datatom.settings import BASE_DIR
from user.models import User
from custom_lib.json_response import render_json
from common import errors


def produce_vcode():
    return str(randint(100000, 1000000))


@call_by_worker
def send_email_code(email):
    vcode = produce_vcode()
    send_mail(
        subject='验证码',
        from_email=None,
        message='您的验证码为：%s' % vcode,
        recipient_list=[email]
    )
    email_key = '-'.join([email, 'vcode'])
    cache.set(email_key, vcode, 120)


# 判断用户使用哪个数据库
def decide_user_use_db(user_name):
    md5_last_char = md5(user_name.encode('utf-8')).hexdigest()[-1]
    if md5_last_char.isdigit():
        return 'node1'
    else:
        return 'node2'


# 生成验证码
def random_code_chr(start, end):
    return chr(random.randint(start, end))


def new_code_str(len_=4):
    code_str = ''
    for _ in range(len_):
        flag = random.randint(0, 2)
        start, end = (
            (ord('a'), ord('z')) if flag == 1 else (ord('A'), ord('Z')) if flag == 2 else (ord('0'), ord('9'))
        )
        code_str += random_code_chr(start, end)
    return code_str


def new_image_code(new_code):
    font_path = os.path.join(BASE_DIR, 'font.ttf')
    image = Image.new('RGB', (100, 40), (100, 100, 0))
    draw = ImageDraw.Draw(image, 'RGB')
    font_color = (0, 20, 100)
    font = ImageFont.truetype(font=font_path, size=30)
    draw.text((5, 5), new_code, font=font, fill=font_color)
    draw.line([(0, 0), (100, 40)], (255, 0, 0), 1)
    for x in range(100):
        draw.point((random.randint(0, 100), random.randint(0, 40)), (0, 0, 255))
    buffer = BytesIO()
    image.save(buffer, 'png')
    return buffer.getvalue()


# 生成cookie的值
def get_cookie_value():
    return uuid4().hex


# 判断cache中是否有用户信息，如果有直接使用，如果没有则从数据库加载，并将信息缓存到cache中
def get_cache_or_update_cache(user_name):
    user_cache_key = '-'.join([user_name, 'user-cache-key'])
    user = cache.get(user_cache_key)
    if user:
        return user
    else:
        user_db = decide_user_use_db(user_name)
        user_object = User.objects.using(user_db).get(user_name=user_name)
        user_object.have_all_authority(user_db)  # 手动执行将用户详情信息绑定到user对象上
        user_object.profile(user_db)  # 手动执行将用户权限信息绑定到user对象上
        cache.set(user_cache_key, user_object, 86400)  # 缓存个人信息86400秒，一天
        return user_object


# 更新数据库并更新缓存
def update_profile_db_and_cache(user_name, new_profile):
    '''
    :param user_name:
    :param new_profile:
    :return: None
    '''
    user_cache_key = '-'.join([user_name, 'user-cache-key'])
    user_db = decide_user_use_db(user_name)
    user_object = User.objects.using(user_db).get(user_name=user_name)
    user_object.have_all_authority(user_db)  # 手动执行将用户详情信息绑定到user对象上
    user_object.profile(user_db)  # 手动执行将用户权限信息绑定到user对象上
    user_object.user_profile.__dict__.update(new_profile)
    user_object.user_profile.save()
    cache.set(user_cache_key, user_object, 86400)


# 上传头像，更新数据库和缓存
def upload_image_updata_db_and_cache(user_name, new_image_path):
    user_cache_key = '-'.join([user_name, 'user-cache-key'])
    user_db = decide_user_use_db(user_name)
    user_object = User.objects.using(user_db).get(user_name=user_name)
    user_object.have_all_authority(user_db)  # 手动执行将用户详情信息绑定到user对象上
    user_object.profile(user_db)  # 手动执行将用户权限信息绑定到user对象上
    user_object.user_profile.__dict__['user_image'] = new_image_path
    user_object.user_profile.save()
    cache.set(user_cache_key, user_object, 86400)


# 更新用户个人的cache
def refresh_user_in_cache(user_name):
    user_cache_key = '-'.join([str(user_name), 'user-cache-key'])
    user_db = decide_user_use_db(user_name)
    user_object = User.objects.using(user_db).get(user_name=user_name)
    user_object.have_all_authority(user_db)  # 手动执行将用户详情信息绑定到user对象上
    user_object.profile(user_db)  # 手动执行将用户权限信息绑定到user对象上
    cache.set(user_cache_key, user_object, 86400)


# 验证用户是否具有一些权限
def check_power(power):
    def deco(view_func):
        def wrap(request):
            user_name = request.session.get('user_name')
            user = get_cache_or_update_cache(user_name)
            if power in user.user_authority_list:
                response = view_func(request)
                return response
            else:
                return render_json(None, errors.DONT_HAVE_POWER)

        return wrap

    return deco


# 查询所有用户，缓存中没有，则从数据库中查询，并写入缓存中
# 考虑一个问题，如果两个SuperAdmin同时登陆的话，使用同一个缓存数据，这样当其中一个超级用户更新用户的数据后是否会有问题（每个超级用户维护自己的一个缓存数据或者增加一个刷新按钮）
def query_all_user_db_or_cache():
    query_all_user_key = "query_all_user_key"
    user_list = cache.get(query_all_user_key)
    if user_list:
        return user_list
    else:
        user_list = list(User.objects.using('node1').all())
        user_list.extend(User.objects.using('node2').all())
        cache.set(query_all_user_key, user_list, 600)  # 缓存10分钟
        return user_list


# 从数据库中刷新cache中用户信息
def refresh_all_user_in_cache():
    query_all_user_key = "query_all_user_key"
    user_list = list(User.objects.using('node1').all())
    user_list.extend(User.objects.using('node2').all())
    cache.set(query_all_user_key, user_list, 600)
