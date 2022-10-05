from django.db import models
from django.contrib.auth import get_user_model


UserModel = get_user_model()


class Poll(models.Model):
    name = models.CharField(max_length=50)


class Vote(models.Model):
    poll = models.ForeignKey(
        to=Poll,
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        to=UserModel,
        on_delete=models.CASCADE,
    )
