from rest_framework import serializers
from django.contrib.auth.models import User
from eatple_app.models import User


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
        )
