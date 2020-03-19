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

        date_range_start = request.query_params.get('date_range_start')
        date_range_end = request.query_params.get('date_range_end')

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

        if(date_range_start != None and date_range_end != None):
            date_range_start = date_range_start.split('-')
            date_range_start = dateNowByTimeZone().replace(
                year=int(date_range_start[0]),
                month=int(date_range_start[1]),
                day=int(date_range_start[2]),
                hour=0, minute=0, second=0, microsecond=0)

            date_range_end = date_range_end.split('-')
            date_range_end = dateNowByTimeZone().replace(
                year=int(date_range_end[0]),
                month=int(date_range_end[1]),
                day=int(date_range_end[2]),
                hour=0, minute=0, second=0, microsecond=0)
        else:
            date_range_start = dateNowByTimeZone() + datetime.timedelta(days=-1)
            date_range_end = dateNowByTimeZone()
            pass

        if(store != None):
            filter.add(Q(store__name__contains=store), filter.OR)

        if(menu != None):
            filter.add(Q(menu__name__contains=store), filter.OR)

        if(method != None):
            filter.add(Q(payment_type=method), filter.OR)

        if(status != None):
            filter.add(Q(payment_status=status), filter.OR)

        orderList = orderList.filter(
            (
                Q(payment_date__gte=date_range_start) &
                Q(payment_date__lt=date_range_end)
            ) &
            filter)[:count]

        response['total'] = orderList.count()
        response['order'] = OrderSerializer(orderList, many=True).data
        response['error_code'] = 200

        return Response(response)
