# Generated by Django 2.1.5 on 2019-01-28 14:17

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('VoteWebCore', '0003_tb_votemulti_tb_votemulti_quest'),
    ]

    operations = [
        migrations.CreateModel(
            name='TB_VoteMulti_Answer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quests_no', models.IntegerField()),
                ('quest_numerate', models.IntegerField()),
                ('answer_numerate', models.IntegerField()),
                ('answer_text', models.CharField(max_length=16)),
            ],
        ),
    ]
