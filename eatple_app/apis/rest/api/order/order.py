# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.user.validation import *
from eatple_app.apis.rest.api.error_table import *

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response

from eatple_app.apis.rest.serializer.order import OrderSerializer


def getAdjustment(orderList, date_range):
    orderList = orderList.order_by('payment_date')
    adjustmentList = []

    if(orderList):
        start_date = orderList.first().payment_date.replace(
            hour=0, minute=0, second=0)

        # Do
        start_date = start_date - datetime.timedelta(days=start_date.weekday())
        end_date = start_date + datetime.timedelta(days=7)
        settlement_date = end_date + datetime.timedelta(days=10)

        inquiryOrderList = orderList.filter(
            Q(payment_date__gte=start_date),
            Q(payment_date__lt=end_date)
        )

        while(inquiryOrderList.count() > 0):
            total_price = 0
            total_order = inquiryOrderList.count()

            for order in inquiryOrderList:
                total_price += order.totalPrice

            supply_price = int(total_price / 1.1)
            surtax_price = total_price - supply_price
            fee = int(total_price * 0.0352)
            settlement_amount = total_price - fee

            adjustmentList.append(
                dict({
                    'settlement_date': settlement_date.strftime('%Y-%m-%d'),
                    'adjustment_date_range': '{} ~ {}'.format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
                    'total_order': total_order,
                    'total_price': '{}원'.format(format(total_price, ",")),
                    'supply_price': '{}원'.format(format(supply_price, ",")),
                    'surtax_price': '{}원'.format(format(surtax_price, ",")),
                    'fee': '{}원'.format(format(fee, ",")),
                    'settlement_amount': '{}원'.format(format(settlement_amount, ",")),
                    'unit': 'won'
                })
            )
            start_date = end_date
            end_date = start_date + datetime.timedelta(days=7)
            settlement_date = end_date + datetime.timedelta(days=10)

            inquiryOrderList = orderList.filter(
                Q(payment_date__gte=start_date),
                Q(payment_date__lt=end_date)
            )
    else:
        pass

    return adjustmentList


def getSurtax(orderList, date_range):
    orderList = orderList.order_by('payment_date')
    surtax = {
        'sales': {},
        'purchase': {}
    }

    if(orderList):
        total_price = 0
        total_order = orderList.count()

        for order in orderList:
            total_price += order.totalPrice

        fee_total_price = int(total_price * 0.0352)
        fee_supply_price = int(fee_total_price / 1.1)
        fee_surtax_price = fee_total_price - fee_supply_price

        surtax['sales'] = dict({
            'date_range': '{} ~ {}'.format(date_range[0].strftime('%Y-%m-%d'), date_range[1].strftime('%Y-%m-%d')),
            'total_order': total_order,
            'total_price': '{}원'.format(format(total_price, ",")),
            'unit': 'won'
        })
        surtax['purchase'] = dict({
            'date_range': '{} ~ {}'.format(date_range[0].strftime('%Y-%m-%d'), date_range[1].strftime('%Y-%m-%d')),
            'total_order': total_order,
            'supply_price': '{}원'.format(format(fee_supply_price, ",")),
            'surtax_price': '{}원'.format(format(fee_surtax_price, ",")),
            'total_price': '{}원'.format(format(fee_total_price, ",")),
            'unit': 'won'
        })

    else:
        pass

    return surtax


def param_valid(param):
    if(param == None or param == ""):
        return False
    else:
        return True


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get']

    def list(self, request):
        orderList = Order.objects.filter(
            ~Q(store=None) &
            ~Q(menu=None)
        )
        response['total'] = orderList.count()
        response['order'] = OrderSerializer(orderList, many=True).data
        response['error_code'] = 200

        return Response(response)

    @action(detail=False, methods=['get'])
    def store(self, request, *args, **kwargs):
        response = {}
        crn = request.query_params.get('crn')
        order_id = request.query_params.get('order_id')
        menu = request.query_params.get('menu')
        store = request.query_params.get('store')
        methodList = request.query_params.getlist('method[]')
        isPaid = request.query_params.get('isPaid')
        isCanceled = request.query_params.get('isCanceled')
        date_range = request.query_params.getlist('date_range[]')

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
            date_range.append(dateNowByTimeZone() -
                              datetime.timedelta(days=(31 * 3)))
            date_range.append(dateNowByTimeZone())

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

        return JsonResponse(response)

    @action(detail=False, methods=['get'])
    def adjustments(self, request, *args, **kwargs):
        response = {}
        crn = request.query_params.get('crn')
        store = request.query_params.get('store')
        date_range = request.query_params.getlist('date_range[]')

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
            date_range.append(dateNowByTimeZone() -
                              datetime.timedelta(days=(31 * 3)))
            date_range.append(dateNowByTimeZone())

        orderList = orderList.filter(
            (
                Q(payment_date__gte=date_range[0]) &
                Q(payment_date__lt=date_range[1])
            ))

        adjustmentList = getAdjustment(orderList, date_range)
        surtax = getSurtax(orderList, date_range)

        response['adjustments'] = adjustmentList
        response['surtax'] = surtax
        response['error_code'] = 200

        return JsonResponse(response)
