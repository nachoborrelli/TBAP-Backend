from django.db import models
from users.models import User
from user_admin.models import Course
from user_admin.models import Organization

class TokenGroup(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='tokens')
    image = models.ImageField(upload_to = 'token_image', default = 'token_image/default.jpg', blank = True, null = True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='token_groups')

    def at_least_one_claimed(self):
        return self.user_tokens.filter(is_claimed=True).exists()

class UserToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_tokens') 
    token_group = models.ForeignKey(TokenGroup, on_delete=models.CASCADE, related_name='user_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    is_claimed = models.BooleanField(default=False)
    tokenId = models.IntegerField(null=True)

    def get_organization(self):
        return self.token_group.course.organization

    def to_dict(self):
        return {
            'id': self.id,
            'user': self.user.id,
            'token_group': self.token_group.id,
            'created_at': self.created_at,
            'is_claimed': self.is_claimed,
            'tokenId': self.tokenId
        }
class Signature(models.Model):
    nonce = models.IntegerField()
    signature = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='signatures')
    token_name = models.CharField(max_length=100)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='signatures')
    uri = models.CharField(max_length=100)
    was_used = models.BooleanField(default=False)

