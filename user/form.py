from django import forms
from user.models import User


class UserEmail(forms.Form):
    user_name = forms.EmailField(max_length=30, min_length=8)


class UserModifyProfile(forms.Form):
    user_nickname = forms.CharField(max_length=8, min_length=1)  # error_messages='昵称不合法'
    sex = forms.ChoiceField(choices=(('F', '男'), ('M', '女')))  # error_messages='请输入正确的性别'

    """
        自定义相关字段的验证
        def clean_user_nickname(self):
        clean_data = super().clean()  # 手动清洗数据
        user_nickname = clean_data.get('user_nickname')
        if xxxx:
            raise forms.ValidationError('min_age>max_age')
        return user_nickname
    """
