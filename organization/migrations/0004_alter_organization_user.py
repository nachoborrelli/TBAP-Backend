# Generated by Django 3.2.18 on 2023-07-04 22:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0003_rename_invitationtoorganization_invitationtobecameuseradmin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='user',
            field=models.OneToOneField(blank=True, on_delete=django.db.models.deletion.CASCADE, related_name='organization', to=settings.AUTH_USER_MODEL),
        ),
    ]
