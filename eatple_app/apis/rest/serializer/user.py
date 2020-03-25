from rest_framework import serializers
from eatple_app.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ()
