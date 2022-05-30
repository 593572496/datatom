# Generated by Django 4.0 on 2022-05-30 08:43

import custom_lib.orm
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Authority',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('power', models.CharField(max_length=10, unique=True, verbose_name='权限')),
            ],
            options={
                'db_table': 'Authority',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_name', models.CharField(max_length=50, unique=True, verbose_name='用户账号')),
                ('user_password', models.CharField(max_length=100, unique=True, verbose_name='账号密码——加密过后')),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='UserAuthority',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.IntegerField()),
                ('Authority_id', models.IntegerField()),
            ],
            options={
                'db_table': 'UserAuthority',
            },
        ),
        migrations.CreateModel(
            name='UserData',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_nickname', models.CharField(default='Husky', max_length=8, verbose_name='昵称')),
                ('user_image', models.CharField(default='D:\\pycharm\\datatom\\media/image/default.png', max_length=200, verbose_name='用户头像')),
                ('sex', models.CharField(choices=[('F', '男'), ('M', '女')], max_length=1, null=True)),
            ],
            options={
                'db_table': 'UserData',
            },
            bases=(models.Model, custom_lib.orm.ModelMixin),
        ),
    ]
