from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class TB_Quiz(models.Model):
    # quiz_id = models.AutoField(primary_key=True)
    quiz_name = models.CharField(max_length=32, default='')
    quiz_type = models.IntegerField()
    quiz_owner = models.ForeignKey(to=User, on_delete=models.SET_NULL, null=True)


class TB_QuizDiscret(models.Model):
    quiz_id = models.ForeignKey(to=TB_Quiz, on_delete=models.CASCADE)
    quiz_no = models.IntegerField()
    quiz_text_question = models.CharField(max_length=256)
    quiz_text_yes = models.CharField(max_length=16)
    quiz_text_no = models.CharField(max_length=16)


class TB_QuizLog(models.Model):
    answ_user_id = models.IntegerField()
    quiz_id = models.IntegerField()
    quiz_no = models.IntegerField()
    result_text = models.CharField(max_length=256)
