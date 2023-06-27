from django.db import models
from users.models import User, SEX_CHOICES

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    birthdate = models.DateField(null=True, blank=True)
    sex = models.CharField(max_length=30, choices=SEX_CHOICES, null=True, blank=True)
    profile_image = models.ImageField(upload_to = 'profile_image', default = 'profile_image/default.jpg', blank = True, null = True)
    identification_type = models.CharField(max_length=20, null=True, blank=True)
    identification_number = models.CharField(max_length=20, null=True, blank=True)
    wallet_address = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = 'Regular User'
        verbose_name_plural = 'Regular Users'

class UserCourses(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='users_courses')
    course = models.ForeignKey('user_admin.Course', on_delete=models.CASCADE, related_name='users_courses')