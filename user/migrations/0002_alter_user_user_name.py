# Generated by Django 4.0 on 2022-05-30 10:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_name',
            field=models.EmailField(max_length=50, unique=True, verbose_name='用户账号（邮箱）'),
        ),
    ]