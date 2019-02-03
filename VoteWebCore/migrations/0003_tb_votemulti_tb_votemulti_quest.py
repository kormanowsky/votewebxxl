# Generated by Django 2.1.5 on 2019-01-28 14:12

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('VoteWebCore', '0002_auto_20190128_1357'),
    ]

    operations = [
        migrations.CreateModel(
            name='TB_VoteMulti',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vote_no', models.IntegerField()),
                ('quests_no', models.IntegerField()),
                ('vote_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='VoteWebCore.TB_Vote')),
            ],
        ),
        migrations.CreateModel(
            name='TB_VoteMulti_Quest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quest_numerate', models.IntegerField()),
                ('quest_text', models.CharField(max_length=16)),
                ('quests_no', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='VoteWebCore.TB_VoteMulti')),
            ],
        ),
    ]
