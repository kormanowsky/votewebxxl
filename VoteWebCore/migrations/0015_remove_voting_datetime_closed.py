# Generated by Django 2.1.5 on 2019-02-06 11:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('VoteWebCore', '0014_auto_20190206_1447'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='voting',
            name='datetime_closed',
        ),
    ]
