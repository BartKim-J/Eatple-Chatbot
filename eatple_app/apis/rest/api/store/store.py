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
        if(crn != None):
            crn = crn.replace('-', '')

            crnFilter = Q()
            if(crn == ADMIN_CRN):
                crnFilter.add(
                    Q(store__crn__CRN_id=crn), crnFilter.AND)
        else:
            response['error_code'] = PARTNER_LOGIN_300_INVALID_CRN.code
            response['error_msg'] = PARTNER_LOGIN_300_INVALID_CRN.message

        infoFilter = Q()

        infoFilter.add(~Q(name__contains='잇플'), infoFilter.AND)

        if(param_valid(id)):
            infoFilter.add(Q(store_id=id), infoFilter.OR)

        if(param_valid(name)):
            infoFilter.add(Q(name__contains=name), infoFilter.OR)

        storeList = Store.objects.filter(
            crnFilter |
            infoFilter
        )

        response['stores'] = StoreSerializer(storeList, many=True).data
        response['error_code'] = 200

        return Response(response)
