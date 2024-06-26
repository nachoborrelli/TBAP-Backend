# Generated by Django 3.2.18 on 2023-08-10 23:28

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organization', '0005_alter_organization_name'),
        ('blockchain', '0006_usertoken_is_claimed'),
    ]

    operations = [
        migrations.CreateModel(
            name='Signature',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nonce', models.IntegerField()),
                ('signature', models.CharField(max_length=128)),
                ('token_name', models.CharField(max_length=100)),
                ('uri', models.CharField(max_length=100)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signatures', to='organization.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='signatures', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.DeleteModel(
            name='NonceTracker',
        ),
        migrations.RenameField(
            model_name='usertoken',
            old_name='token',
            new_name='token_group',
        ),
    ]
