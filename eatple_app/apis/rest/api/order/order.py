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


def param_valid(param):
    if(param == None or param == ""):
        return False
    else:
        return True


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        response = {}
        crn = request.query_params.get('crn')
        order_id = request.query_params.get('order_id')
        menu = request.query_params.get('menu')
        store = request.query_params.get('store')
        methodList = request.query_params.getlist('method[]')
        isPaid = request.query_params.get('isPaid')
        isCanceled = request.query_params.get('isCanceled')
        count = request.query_params.get('count')

        date_range = request.query_params.getlist('date_range[]')

        print('CRN', crn)
        print('ORDER ID', order_id)
        print('STORE', store)
        print('MENU', menu)
        print('METHOD', methodList)
        print('PAID', isPaid)
        print('CANCELED', isCanceled)
        print(count)
        print('DATE RANGE', date_range)

        if(crn != None):
            crn = crn.replace('-', '')
        else:
            response['error_code'] = PARTNER_LOGIN_300_INVALID_CRN.code
            response['error_msg'] = PARTNER_LOGIN_300_INVALID_CRN.message

            return Response(response)

        orderList = Order.objects.filter(
            Q(store__crn__CRN_id=crn) &
            ~Q(store=None) &
            ~Q(menu=None) &
            (
                Q(payment_status=EATPLE_ORDER_STATUS_PAID) |
                Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED)
            )
        )

        if(param_valid(count) == False):
            count = 30

        if(date_range and len(date_range) >= 2):
            date_range[0] = date_range[0].split('-')
            date_range[0] = dateNowByTimeZone().replace(
                year=int(date_range[0][0]),
                month=int(date_range[0][1]),
                day=int(date_range[0][2]),
                hour=0, minute=0, second=0, microsecond=0)

            date_range[1] = date_range[1].split('-')
            date_range[1] = dateNowByTimeZone().replace(
                year=int(date_range[1][0]),
                month=int(date_range[1][1]),
                day=int(date_range[1][2]),
                hour=0, minute=0, second=0, microsecond=0)

            if(date_range[0] > date_range[1]):
                temp = date_range[0]
                date_range[0] = date_range[1]
                date_range[1] = temp

        else:
            date_range.append(dateNowByTimeZone() +
                              datetime.timedelta(days=-30))
            date_range.append(dateNowByTimeZone())
            pass

        infoFilter = Q()
        if(param_valid(order_id)):
            infoFilter.add(
                Q(order_id__contains=order_id.upper()), infoFilter.AND)

        if(param_valid(store)):
            infoFilter.add(Q(store__name__contains=store), infoFilter.OR)

        if(param_valid(menu)):
            infoFilter.add(Q(menu__name__contains=menu), infoFilter.OR)

        methodFilter = Q()
        if(param_valid(methodList)):
            for methodValue in methodList:
                for item in dict(ORDER_PAYMENT_TYPE).items():
                    if(methodValue == item[1]):
                        methodFilter.add(
                            Q(payment_type=item[0]), methodFilter.OR)
                        break

        statusFilter = Q()
        if(param_valid(isPaid) and isPaid == 'true'):
            statusFilter.add(
                Q(payment_status=EATPLE_ORDER_STATUS_PAID), statusFilter.OR)

        if(param_valid(isCanceled) and isCanceled == 'true'):
            statusFilter.add(
                Q(payment_status=EATPLE_ORDER_STATUS_CANCELLED), statusFilter.OR)

        orderList = orderList.filter(
            (
                Q(payment_date__gte=date_range[0]) &
                Q(payment_date__lt=date_range[1])
            ) &
            methodFilter &
            statusFilter &
            infoFilter)

        response['total'] = orderList.count()
        response['order'] = OrderSerializer(orderList, many=True).data
        response['error_code'] = 200

        return Response(response)
