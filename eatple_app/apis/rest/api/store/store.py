from eatple_app.apis.rest.define import *
from eatple_app.apis.rest.serializer.store import StoreSerializer


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
        else:
            response['error_code'] = PARTNER_LOGIN_300_INVALID_CRN.code
            response['error_msg'] = PARTNER_LOGIN_300_INVALID_CRN.message

        adminFilter = Q()
        if(crn == ADMIN_CRN):
            pass
        else:
            adminFilter.add(Q(crn__CRN_id=crn), adminFilter.AND)
            
        if(param_valid(id)):
            filter.add(Q(store_id=id), filter.OR)

        if(param_valid(name)):
            filter.add(Q(name_contains=name), filter.OR)

        storeList = Store.objects.filter(adminFilter & filter)

        response['stores'] = StoreSerializer(storeList, many=True).data
        response['error_code'] = 200

        return Response(response)
