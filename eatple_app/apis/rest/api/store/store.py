# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.user.validation import *
from eatple_app.apis.rest.api.error_table import *

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions

from eatple_app.apis.rest.serializer.store import StoreSerializer


def param_valid(param):
    if(param == None or param == ""):
        return False
    else:
        return True


class StoreViewSet(viewsets.ModelViewSet):
    queryset = Store.objects.all()
    serializer_class = StoreSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        response = {}
        crn = request.query_params.get('crn')
        id = request.query_params.get('id')
        name = request.query_params.get('name')

        filter = Q()
        if(crn != None):
            crn = crn.replace('-', '')
            filter.add(Q(crn__CRN_id=crn), filter.OR)
        else:
            response['error_code'] = PARTNER_LOGIN_300_INVALID_CRN.code
            response['error_msg'] = PARTNER_LOGIN_300_INVALID_CRN.message

        if(param_valid(id)):
            filter.add(Q(store_id=id), filter.OR)

        if(param_valid(name)):
            filter.add(Q(name_contains=name), filter.OR)

        storeList = Store.objects.filter(filter)

        response['stores'] = StoreSerializer(storeList, many=True).data
        response['error_code'] = 200

        return Response(response)
