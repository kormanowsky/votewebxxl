# Generated by Django 2.1.5 on 2019-02-06 20:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VoteWebCore', '0002_remove_report_status'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.IntegerField(default=0),
        ),
    ]
