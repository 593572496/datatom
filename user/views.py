from django.http import HttpResponse
from user.form import UserForm
from custom_lib.json_response import render_json
from common import errors


def register(request):
    if UserForm(request.POST).is_valid():
        pass  # send_email_code()
    else:
        return render_json(UserForm.errors, errors.EMAIL_FORMAT_ERROR)
