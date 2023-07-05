from django.db import models
from users.models import User
from user_admin.models import Course


#TODO Agregar nonce tracker

class TokenGroup(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tokens')
    image = models.ImageField(upload_to = 'token_image', default = 'token_image/default.jpg', blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_groups')


class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tokens') 
    token = models.ForeignKey(TokenGroup, on_delete=models.CASCADE, related_name='user_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
