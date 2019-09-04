# Generated by Django 2.2.4 on 2019-09-04 08:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store_app', '0048_order_update_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.CharField(choices=[('주문 확인중', '주문 확인중'), ('주문 완료', '주문 완료'), ('픽업 준비중', '픽업 준비중'), ('픽업 완료', '픽업 완료'), ('주문 만료', '주문 만료'), ('주문 취소', '주문 취소')], default='주문 확인중', max_length=255),
        ),
    ]