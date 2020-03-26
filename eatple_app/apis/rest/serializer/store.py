from rest_framework import serializers
from eatple_app.models import Store


class StoreSerializer(serializers.ModelSerializer):
    
    crn = serializers.SerializerMethodField()
    def get_crn(self, obj):
        crn_form = obj.crn
        return '{UID}-{CC}-{SN}{VN}'.format(
            UID=crn_form.UID,
            CC=crn_form.CC,
            SN=crn_form.SN,
            VN=crn_form.VN
        )
    
    class Meta:
        model = Store
        exclude = ()
