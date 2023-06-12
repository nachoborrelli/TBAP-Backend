import string
import random
import requests
from django.contrib.auth import get_user_model
User = get_user_model()

def get_random_string(length):
    characters = string.ascii_letters + string.digits
    result_str = ''.join(random.choice(characters) for i in range(length))
    return result_str


def get_user_email(access_token, url='https://127.0.0.1:8001/userinfo/'):
    headers = {'Authorization': f'Bearer {access_token}'}
    r = requests.get(url, headers=headers, verify=False)
    return r.json()['email']


def create_user_without_password(username):
    user = User(username=username, email=username)
    user.set_unusable_password()
    user.save()
    return user