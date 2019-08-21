# Generated by Django 2.2.4 on 2019-08-21 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0010_remove_menu_store_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='menu',
            name='store_name',
            field=models.CharField(default='<django.db.models.fields.related.ForeignKey>', max_length=255),
        ),
        migrations.AlterField(
            model_name='store',
            name='store_name',
            field=models.CharField(help_text='상호명', max_length=255),
        ),
    ]
