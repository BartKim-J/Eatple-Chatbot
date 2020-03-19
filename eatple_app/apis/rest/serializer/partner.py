from rest_framework import serializers
from django.contrib.auth.models import User
from eatple_app.models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        fields = (
            'app_user_id',
            'nickname',
            'email',
        )
