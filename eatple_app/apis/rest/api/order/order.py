# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.user.validation import *
from eatple_app.apis.rest.api.error_table import *

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions

from eatple_app.apis.rest.serializer.order import OrderSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        response = {}
        menu = request.query_params.get('menu')
        store = request.query_params.get('store')
        method = request.query_params.get('method')
        status = request.query_params.get('status')
        count = request.query_params.get('count')

        orderList = Order.objects.filter(
            ~Q(store=None) &
            ~Q(menu=None) &
            (
                Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
                Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)
            )
        )

        filter = Q()
        if(count == None):
            count = 30

        if(store != None):
            filter.add(Q(store__name__contains=store), filter.OR)

        if(menu != None):
            filter.add(Q(menu__name__contains=store), filter.OR)

        if(method != None):
            filter.add(Q(payment_type=method), filter.OR)

        if(status != None):
            filter.add(Q(payment_status=status), filter.OR)

        orderList = orderList.filter(filter)[:count]

        response['total'] = orderList.count()
        response['order'] = OrderSerializer(orderList, many=True).data
        response['error_code'] = PARTNER_LOGIN_200_SUCCESS.code
        response['error_msg'] = PARTNER_LOGIN_200_SUCCESS.message

        return Response(response)
