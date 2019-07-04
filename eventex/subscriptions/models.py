import hashlib
from enum import unique

from django.db import models
from django.db.models.fields import CharField
from django.forms.fields import CharField
from pygments.lexer import default


class Subscription(models.Model):
    name = models.CharField('nome', max_length=100)
    cpf = models.CharField('CPF', max_length=11)
    email = models.EmailField('e-mail', unique=True)
    phone = models.CharField('telefone', max_length=20)
    created_at = models.DateTimeField('criado em', auto_now_add=True)
    hash_url = models.CharField('URL', max_length=32, null=True)

    class Meta:
        verbose_name_plural = 'inscrições'
        verbose_name = 'inscrição'
        ordering = ('-created_at',)

    def __str__(self):
        return self.name
