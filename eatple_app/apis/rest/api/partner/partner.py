# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.error_table import *

from django.core import serializers
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from eatple_app.apis.rest.serializer.partner import PartnerSerializer
from eatple_app.apis.rest.serializer.store import StoreSerializer

class PartnerViewSet(viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    http_method_names = ['get', 'post', 'patch', 'delete']

    @swagger_auto_schema(
        operation_description="파트너",
        responses={
            200:
                PARTNER_LOGIN_200_SUCCESS.as_md(),
            400:
                PARTNER_LOGIN_300_INVALID_CRN.as_md() +
                PARTNER_LOGIN_301_INVALID_TOKEN.as_md() +
                PARTNER_LOGIN_310_NULL_CRN.as_md() +
                PARTNER_LOGIN_311_NULL_TOKEN.as_md()
        }
    )
    def list(self, request, *args, **kwargs):
        print(request.body)

        response = {}
        crn = request.query_params.get('crn')
        token = request.query_params.get('token')

        if(crn == None):
            response['error_code'] = PARTNER_LOGIN_311_NULL_TOKEN.code
            response['error_msg'] = PARTNER_LOGIN_311_NULL_TOKEN.message

            return Response(response)
        elif(token == None):
            response['error_code'] = PARTNER_LOGIN_311_NULL_TOKEN.code
            response['error_msg'] = PARTNER_LOGIN_311_NULL_TOKEN.message

            return Response(response)

        try:
            storeList = Store.objects.filter(crn__CRN_id=crn)
        except Store.DoesNotExist as ex:
            response['error_code'] = PARTNER_LOGIN_300_INVALID_CRN.code
            response['error_msg'] = PARTNER_LOGIN_300_INVALID_CRN.message

            return Response(response)

        token_auth = False
        for store in storeList:
            checker = store.phone_number.as_national.split('-')[2]
            if(checker == token):
                partnerStore = store
                token_auth = True

        if(token_auth == False):
            response['error_code'] = PARTNER_LOGIN_301_INVALID_TOKEN.code
            response['error_msg'] = PARTNER_LOGIN_301_INVALID_TOKEN.message

            return Response(response)

        try:
            partner = Partner.objects.get(
                phone_number=partnerStore.phone_number)
        except Partner.DoesNotExist as ex:
            response['error_code'] = PARTNER_LOGIN_300_INVALID_CRN.code
            response['error_msg'] = PARTNER_LOGIN_300_INVALID_CRN.message

            return Response(response)

        response['stores'] = StoreSerializer(storeList, many=True).data
        response['partner'] = PartnerSerializer(partner).data
        response['error_code'] = PARTNER_LOGIN_200_SUCCESS.code
        response['error_msg'] = PARTNER_LOGIN_200_SUCCESS.message

        return Response(response)

    def post(self, request):
        print("create")
        response = {}

        response['error_code'] = PARTNER_LOGIN_200_SUCCESS.code
        response['error_msg'] = PARTNER_LOGIN_200_SUCCESS.message

        return Response(response)

    def destroys(self, request, pk=None):
        print("destroys")
        response['error_code'] = PARTNER_LOGIN_200_SUCCESS.code
        response['error_msg'] = PARTNER_LOGIN_200_SUCCESS.message

        return Response(response)
