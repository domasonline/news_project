# Generated by Django 2.1.5 on 2019-03-29 09:51

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0005_auto_20190329_1150'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newspost',
            name='down_votes',
        ),
        migrations.RemoveField(
            model_name='newspost',
            name='up_votes',
        ),
        migrations.AlterField(
            model_name='postvotes',
            name='user_id',
            field=models.ForeignKey(default=(), on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
