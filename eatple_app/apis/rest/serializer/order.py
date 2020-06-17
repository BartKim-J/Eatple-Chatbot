from rest_framework import serializers
from eatple_app.models import Order
from eatple_app.system.model_type import *


class OrderSerializer(serializers.ModelSerializer):
    menu = serializers.CharField(max_length=200)
    store = serializers.CharField(max_length=200)
    totalPrice = serializers.SerializerMethodField()

    pickup_time = serializers.DateTimeField(
        format="%y년 %m월 %d일", required=False, read_only=True)
    payment_date = serializers.DateTimeField(
        format="%y년 %m월 %d일", required=False, read_only=True)

    payment_type = serializers.SerializerMethodField()
    payment_status = serializers.SerializerMethodField()

    user = serializers.SerializerMethodField()
    app_user_id = serializers.SerializerMethodField()
    phone_number = serializers.SerializerMethodField()

    def get_payment_type(self, obj):
        return dict(ORDER_PAYMENT_TYPE)[obj.payment_type]

    def get_payment_status(self, obj):
        return dict(EATPLE_ORDER_STATUS)[obj.payment_status]

    def get_pickup_time(self, obj):
        return obj.payment_date

    def get_totalPrice(self, obj):
        # return '{}원'.format(format(obj.totalPrice, ","))
        return '{}원'.format(format(obj.menu.price, ","))

    def get_user(self, obj):
        return obj.ordersheet.user.nickname

    def get_app_user_id(self, obj):
        return obj.ordersheet.user.app_user_id

    def get_phone_number(self, obj):
        return obj.ordersheet.user.phone_number.as_national

    class Meta:
        model = Order
        exclude = ()
