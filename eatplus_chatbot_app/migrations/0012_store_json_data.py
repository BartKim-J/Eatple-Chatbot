# Generated by Django 2.2.4 on 2019-08-19 10:08

from django.db import migrations
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        ('eatplus_chatbot_app', '0011_auto_20190819_1856'),
    ]

    operations = [
        migrations.AddField(
            model_name='store',
            name='json_data',
            field=jsonfield.fields.JSONField(default={}),
        ),
    ]
