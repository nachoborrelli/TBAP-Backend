from django.db import models
from users.models import User, SEX_CHOICES
from organization.models import Organization

class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admin')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='admins')


class Course(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)


class AdminCourses(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admins_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='admins_courses')

class InvitationToCourse(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Invitation to Course'
        verbose_name_plural = 'Invitations to Courses'