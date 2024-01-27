
from django.db.models.signals import post_delete
from django.dispatch import receiver

from django.db import models
from users.models import User
from organization.models import Organization


class Admin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='admins')


class Course(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='courses')

    def at_least_one_claimed(self):
        for token in self.tokens.all():
            if token.at_least_one_claimed():
                return True
        return False


class AdminCourses(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='admins_courses')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='admins_courses')


class InvitationToCourseAsUser(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='invitations_as_user')
    email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Invitation to Course as User'
        verbose_name_plural = 'Invitations to Courses as Users'



# class InvitationToCourseAsAdmin(models.Model):
#     STATUS_CHOICES = (
#         ('Pending', 'Pending'),
#         ('Accepted', 'Accepted'),
#         ('Rejected', 'Rejected'),
#     )

#     course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='invitations_as_admin')
#     admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='invitations_as_admin')
#     status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         verbose_name = 'Invitation to Course as Admin'
#         verbose_name_plural = 'Invitations to Courses as Admins'
        

# @receiver(post_delete, sender=Course)
# def delete_admins_courses(sender, instance, **kwargs):
#     AdminCourses.objects.filter(course=instance).delete()

    
