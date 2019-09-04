# Generated by Django 2.2.4 on 2019-09-04 06:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0040_auto_20190904_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='menuInstance',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='store_app.Menu'),
        ),
        migrations.AlterField(
            model_name='order',
            name='storeInstance',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='store_app.Store'),
        ),
        migrations.AlterField(
            model_name='order',
            name='userInstance',
            field=models.ForeignKey(blank=True, default=1, on_delete=django.db.models.deletion.DO_NOTHING, to='store_app.User'),
        ),
    ]