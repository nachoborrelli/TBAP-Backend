# Generated by Django 3.2.18 on 2023-06-25 22:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('user_admin', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='InvitationToCourseAsAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_as_admin', to='user_admin.course')),
            ],
            options={
                'verbose_name': 'Invitation to Course as Admin',
                'verbose_name_plural': 'Invitations to Courses as Admins',
            },
        ),
        migrations.CreateModel(
            name='InvitationToCourseAsUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Accepted', 'Accepted'), ('Rejected', 'Rejected')], default='Pending', max_length=10)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitations_as_user', to='user_admin.course')),
            ],
            options={
                'verbose_name': 'Invitation to Course as User',
                'verbose_name_plural': 'Invitations to Courses as Users',
            },
        ),
        migrations.DeleteModel(
            name='InvitationToCourse',
        ),
    ]
