# Generated by Django 2.1.5 on 2019-02-06 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VoteWebCore', '0012_auto_20190206_1444'),
    ]

    operations = [
        migrations.AlterField(
            model_name='voting',
            name='datetime_closed',
            field=models.DateTimeField(default=None, null=True),
        ),
    ]
