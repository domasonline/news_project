# Generated by Django 2.1.5 on 2019-04-06 08:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_auto_20190406_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='search_settings',
            field=models.IntegerField(choices=[(1, 'OR Search results'), (2, 'AND Search results')], default=1),
        ),
    ]
