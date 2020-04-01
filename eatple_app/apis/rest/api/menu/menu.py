from eatple_app.apis.rest.define import *

from eatple_app.apis.rest.serializer.menu import MenuSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        response = {}
        crn = request.query_params.get('crn')
        store = request.query_params.get('store')
        id = request.query_params.get('id')
        name = request.query_params.get('name')

        filter = Q()
        if(crn != None):
            crn = crn.replace('-', '')
        else:
            response['error_code'] = PARTNER_LOGIN_300_INVALID_CRN.code
            response['error_msg'] = PARTNER_LOGIN_300_INVALID_CRN.message

        if(param_valid(store)):
            filter.add(Q(store__id=store), filter.AND)

        if(param_valid(id)):
            filter.add(Q(menu_id=id), filter.AND)

        if(param_valid(name)):
            filter.add(Q(name_contains=name), filter.AND)

        menuList = Menu.objects.filter(filter)

        response['menus'] = MenuSerializer(menuList, many=True).data
        response['error_code'] = 200

        return Response(response)
