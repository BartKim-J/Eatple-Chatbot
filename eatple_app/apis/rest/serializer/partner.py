from rest_framework import serializers
from eatple_app.models import Partner


class PartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Partner
        exclude = ()
