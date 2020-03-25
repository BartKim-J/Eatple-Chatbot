from rest_framework import serializers
from eatple_app.models import Store


class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Store
        exclude = ()
