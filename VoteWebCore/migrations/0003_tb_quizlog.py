# Generated by Django 2.1.5 on 2019-01-22 07:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('VoteWebCore', '0002_tb_quizdiscret'),
    ]

    operations = [
        migrations.CreateModel(
            name='TB_QuizLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('answ_user_id', models.IntegerField()),
                ('quiz_id', models.IntegerField()),
                ('quiz_no', models.IntegerField()),
                ('result_text', models.CharField(max_length=256)),
            ],
        ),
    ]
