from rest_framework import serializers
from django.contrib.auth.models import User
from eatple_app.models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        fields = (
            'id',
            'store_id',
            'name',
            'addr',
            'owner',
            'phone_number',
            'status',
            'type',
            'area',
            'logo',
        )
