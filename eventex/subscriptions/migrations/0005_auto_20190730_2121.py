# Generated by Django 2.2.3 on 2019-07-31 00:21

from django.db import migrations, models
import eventex.subscriptions.validators


class Migration(migrations.Migration):

    dependencies = [
        ('subscriptions', '0004_auto_20190718_1744'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='cpf',
            field=models.CharField(max_length=11, validators=[eventex.subscriptions.validators.validate_cpf], verbose_name='CPF'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='email',
            field=models.EmailField(blank=True, max_length=254, unique=True, verbose_name='e-mail'),
        ),
        migrations.AlterField(
            model_name='subscription',
            name='phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='telefone'),
        ),
    ]