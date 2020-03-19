# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.error_table import *

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions

from eatple_app.apis.rest.serializer.partner import PartnerSerializer


class Partner(viewsets.ModelViewSet):
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
        
        response['error_code'] = PARTNER_LOGIN_200_SUCCESS.code
        response['error_msg'] = PARTNER_LOGIN_200_SUCCESS.message

        return Response(response)
