import os

from django.conf import settings
from django.db import models
from custom_lib.orm import ModelMixin

user_image_default_path = os.path.join(settings.BASE_DIR, r'media\image\default.png')


class User(models.Model):
    user_name = models.EmailField(max_length=50, null=False, unique=True, verbose_name='用户账号（邮箱）')
    user_password = models.CharField(max_length=100, null=False, unique=False, verbose_name='账号密码——加密过后')

    def profile(self, user_db):
        """用户的详细信息"""
        if not hasattr(self, 'user_profile'):
            self.user_profile, _ = UserData.objects.using(user_db).get_or_create(pk=self.id)
        return self.user_profile

    def have_all_authority(self, user_db):
        """用户的所有权限"""
        if not hasattr(self, 'user_role_list'):
            user_authority_list = UserAuthority.objects.using(user_db).filter(user_id=self.id).all()
            self.user_authority_list = [Authority.objects.using(user_db).get(pk=authority.authority_id).power for
                                        authority in user_authority_list]
        return self.user_authority_list

    class Meta:
        db_table = 'user'


class UserData(models.Model, ModelMixin):
    user_nickname = models.CharField(max_length=8, default='Husky', verbose_name='昵称')
    user_image = models.CharField(max_length=200, default=user_image_default_path, verbose_name='用户头像')
    sex = models.CharField(choices=(('F', '男'), ('M', '女')), null=True, max_length=1)

    class Meta:
        db_table = 'UserData'


class Authority(models.Model):
    """SuperAdmin拥有所有的权限（上传，删除，修改补丁信息，修改用户权限），
        Admin 拥有（上传，修改权限），
        '' 仅拥有浏览的权限，
    """
    power = models.CharField(max_length=10, null=False, unique=True, verbose_name='权限')

    class Meta:
        db_table = "Authority"


class UserAuthority(models.Model):
    user_id = models.IntegerField()
    authority_id = models.IntegerField()

    @classmethod  # 给用户添加权限
    def user_add_authority(cls, user_id, authority_id, user_db):
        cls.objects.using(user_db).get_or_create(user_id=user_id, authority_id=authority_id)

    @classmethod  # 删除用户权限
    def user_remove_authority(cls, user_id, authority_id, user_db):
        cls.objects.using(user_db).filter(user_id=user_id, authority_id=authority_id).delete()

    class Meta:
        db_table = 'UserAuthority'
