# define
from eatple_app.define import *
# Django Library
from django.contrib.gis.db import models
from django.conf import settings
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django_mysql.models import Model
from django.core.validators import MaxValueValidator, MinValueValidator


class Survey(models.Model):
    class Meta:
        verbose_name = "설문 조사"
        verbose_name_plural = "설문 조사"

    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        null=True,
        verbose_name="사용자"
    )

    type = models.CharField(
        max_length=WORD_LENGTH,
        default=SURVEY_TYPE_REQUEST,
        choices=SURVEY_TYPE,
        verbose_name="설문 타입"
    )

    answer = models.TextField(
        blank=True,
        verbose_name="응답"
    )

    update_date = models.DateTimeField(
        auto_now=True,
        verbose_name="마지막 수정일"
    )

    create_date = models.DateTimeField(
        default=timezone.now,
        verbose_name="생성일자"
    )

    def apply(self, user, type, answer):
        try:
            self.user = user
            self.type = type
            self.answer = answer
            self.save()
            return True
        except Exception as ex:
            print(ex)
            return False
