from rest_framework import serializers
from eatple_app.models import Partner

ADMIN_CI = 'r+cRMvxrCGOBfEZBSV166Z6474PQayM8H5K0CTOZBaK2eIoddFcH/EVc+nPf6MEfWArJPTctE55fqEq7iUu+5w=='
ADMIN_CRN = '255-87-01463'


class PartnerSerializer(serializers.ModelSerializer):
    crn = serializers.SerializerMethodField()

    def get_crn(self, obj):
        crn_form = obj.store.crn
        return '{UID}-{CC}-{SN}{VN}'.format(
            UID=crn_form.UID,
            CC=crn_form.CC,
            SN=crn_form.SN,
            VN=crn_form.VN
        )

    class Meta:
        model = Partner
        exclude = ()


class PartnerAdminSerializer(serializers.ModelSerializer):
    crn = serializers.SerializerMethodField()

    def get_crn(self, obj):
        return ADMIN_CRN

    class Meta:
        model = Partner
        exclude = ()
