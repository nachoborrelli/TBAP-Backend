# Generated by Django 3.2.18 on 2023-08-10 23:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0007_auto_20230810_2328'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signature',
            name='signature',
            field=models.TextField(),
        ),
    ]
