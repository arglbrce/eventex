from django.db import models
from django.db.models.fields import CharField
from django.forms.fields import CharField


class Subscription(models.Model):
    name = models.CharField(max_length=100)
    cpf = models.CharField(max_length=11)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
