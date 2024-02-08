from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    # add additional fields in here
    pass

    def __str__(self):
        return self.username
    
    @property
    def is_organization(self):
        return hasattr(self, 'organization')

    @property 
    def is_admin(self):
        from user_admin.models import Admin
        return Admin.objects.filter(user=self).exists()


SEX_CHOICES = (
        ('Masculino','Masculino'),
        ('Femenino','Femenino'),
        ('Otro','Otro'),
        ('Prefiero no decirlo','Prefiero no decirlo'),
    )



class TokenRecovery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=6, default='')
    created_at = models.DateTimeField(auto_now_add=True)


# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     from regular_user.models import UserProfile
#     if created and not hasattr(instance, 'user_profile'):
#         UserProfile.objects.create(user=instance)