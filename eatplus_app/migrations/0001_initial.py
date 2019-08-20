# Generated by Django 2.2.4 on 2019-08-20 07:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Store',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('store_name', models.CharField(help_text='상호명', max_length=255)),
                ('store_addr', models.CharField(help_text='주소', max_length=255)),
                ('owner_name', models.CharField(help_text='가맹주', max_length=255)),
                ('store_logo', models.ImageField(blank=True, upload_to='eatplus_chatot_app/DB/logo_img')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]