# Generated by Django 3.1.4 on 2020-12-18 21:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20201218_2201'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='producttonode',
            name='comment',
        ),
    ]