from rest_framework import serializers
from eatple_app.models import Menu


class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        exclude = ()
