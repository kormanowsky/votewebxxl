from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class TB_Vote(models.Model):
    # quiz_id = models.AutoField(primary_key=True)
    vote_name = models.CharField(max_length=32, default='')
    vote_type = models.IntegerField()
    vote_owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)

    # it was vote type
    VT_DISCRET = 0
    VT_MULTI = 1


class TB_VoteDiscret(models.Model):
    vote_id = models.ForeignKey(to=TB_Vote, on_delete=models.CASCADE)
    vote_no = models.IntegerField()
    vote_text_question = models.CharField(max_length=256)
    vote_text_yes = models.CharField(max_length=16)
    vote_text_no = models.CharField(max_length=16)


class TB_VoteLog(models.Model):
    answ_user_id = models.IntegerField()
    vote_id = models.IntegerField()
    vote_no = models.IntegerField()
    answer_no = models.IntegerField(default=-1)


class TB_VoteMulti(models.Model):
    vote_id = models.ForeignKey(to=TB_Vote, on_delete=models.CASCADE)
    # vote_no = models.IntegerField()
    quests_no = models.IntegerField()


class TB_VoteMulti_Quest(models.Model):
    quests_no = models.OneToOneField(to=TB_VoteMulti, on_delete=models.CASCADE)
    quest_numerate = models.IntegerField()
    quest_text = models.CharField(max_length=16)


class TB_VoteMulti_Answer(models.Model):
    quests_no = models.IntegerField()
    quest_numerate = models.IntegerField()
    answer_numerate = models.IntegerField()
    answer_text = models.CharField(max_length=16)
