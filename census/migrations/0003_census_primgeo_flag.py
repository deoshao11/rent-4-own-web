# Generated by Django 3.0.4 on 2020-05-23 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('census', '0002_auto_20200523_2008'),
    ]

    operations = [
        migrations.AddField(
            model_name='census',
            name='primgeo_flag',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]