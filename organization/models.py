from django.db import models
from users.models import User

# Create your models here.
class Organization(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='organization') #founder
    name = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    logo = models.ImageField(upload_to = 'organization_logo', default = 'organization_logo/default.jpg', blank = True, null = True)



class InvitationToOrganization(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )

    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='invitations')
    email = models.EmailField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Invitation'
        verbose_name_plural = 'Invitations'