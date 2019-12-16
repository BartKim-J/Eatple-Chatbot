from rest_framework import serializers
from django.contrib.auth.models import User
from eatple_app.models import Order

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = (
            'order_id', 
            'store', 
            'menu', 
            'totalPrice', 
            'count', 
            'pickup_time',
            
            'payment_status',
            'status',
            
            'update_date',
            'order_date',
        )
