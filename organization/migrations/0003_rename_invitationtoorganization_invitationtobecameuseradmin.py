# Generated by Django 3.2.18 on 2023-06-25 22:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0002_organization_created_at'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='InvitationToOrganization',
            new_name='InvitationToBecameUserAdmin',
        ),
    ]
