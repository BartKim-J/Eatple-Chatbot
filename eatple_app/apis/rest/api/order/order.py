from eatple_app.apis.rest.define import *

from eatple_app.apis.rest.serializer.order import OrderSerializer


"""

0: 월
1: 화
2: 수
3: 목
4: 금
5: 토
6: 일

"""


def getAdjustment(orderList, date_range):
    orderList = orderList.order_by('payment_date')
    adjustmentList = []
    adjustmentExcel = []

    adjustment_total_price = 0
    adjustment_supply_price = 0
    adjustment_surtax_price = 0
    adjustment_fee = 0
    adjustment_settlement_amount = 0

    if(orderList):
        print(date_range[0], date_range[1])

        date_range_start = date_range[0].replace(
            hour=0, minute=0, second=0)
        date_range_end = date_range[1].replace(
            hour=0, minute=0, second=0)

        start_date = date_range_start

        # Do
        start_date = start_date - \
            datetime.timedelta(days=5 - start_date.weekday())
        end_date = start_date.replace(
            hour=23, minute=59, second=59, microsecond=0) + datetime.timedelta(days=6)
        settlement_date = end_date.replace(
            hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=10)

        inquiryOrderList = orderList.filter(
            Q(payment_date__gte=start_date),
            Q(payment_date__lt=end_date)
        )

        while(start_date <= date_range_end):
            total_order = inquiryOrderList.count()
            inquiry_total_price = 0
            inquiry_supply_price = 0
            inquiry_surtax_price = 0
            inquiry_fee = 0
            inquiry_settlement_amount = 0

            if(date_range_start <= settlement_date and settlement_date <= date_range_end):
                for order in inquiryOrderList:
                    total_price = order.totalPrice
                    supply_price = round(total_price / 1.1)
                    surtax_price = total_price - supply_price
                    if(order.type == ORDER_TYPE_B2B):
                        fee = int(total_price * FEE_CONST)
                    else:
                        if(dateByTimeZone(order.payment_date) < FEE_CHANGE_DATE):
                            fee = int(total_price * FEE_CONST_BEFORE)
                        else:
                            fee = int(total_price * FEE_CONST)
                    settlement_amount = total_price - fee

                    # inquiry
                    inquiry_total_price += total_price
                    inquiry_supply_price += supply_price
                    inquiry_surtax_price += surtax_price
                    inquiry_fee += fee
                    inquiry_settlement_amount += settlement_amount

                    # all
                    adjustment_total_price += total_price
                    adjustment_supply_price += supply_price
                    adjustment_surtax_price += surtax_price
                    adjustment_fee += fee
                    adjustment_settlement_amount += settlement_amount

                    # push body on excel
                    adjustmentExcel.append(
                        dict({
                            'ID': order.id,
                            '결제일': order.payment_date.strftime('%Y-%m-%d'),
                            '정산일': settlement_date.strftime('%Y-%m-%d'),
                            '주문번호': order.order_id,
                            '상점': order.store.name,
                            '메뉴': order.menu.name,
                            '주문 타입': dict(ORDER_TYPE)[order.type],
                            '결제수단': '신용카드',
                            '주문 금액': total_price,
                            '공급가액': supply_price,
                            '부가세': surtax_price,
                            '수수료': fee,
                            '정산금액': settlement_amount,
                        })
                    )
                    total_price += order.totalPrice

                if(inquiryOrderList):
                    adjustmentList.append(
                        dict({
                            'settlement_date': settlement_date.strftime('%Y-%m-%d'),
                            'adjustment_date_range': '{} ~ {}'.format(start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d')),
                            'total_order': total_order,
                            'total_price': '{}원'.format(format(inquiry_total_price, ",")),
                            'supply_price': '{}원'.format(format(inquiry_supply_price, ",")),
                            'surtax_price': '{}원'.format(format(inquiry_surtax_price, ",")),
                            'fee': '{}원'.format(format(inquiry_fee, ",")),
                            'settlement_amount': '{}원'.format(format(inquiry_settlement_amount, ",")),
                            'unit': 'won'
                        })
                    )
            else:
                pass

            start_date = end_date.replace(
                hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
            end_date = start_date.replace(
                hour=23, minute=59, second=59, microsecond=0) + datetime.timedelta(days=6)
            settlement_date = end_date.replace(
                hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=10)

            inquiryOrderList = orderList.filter(
                Q(payment_date__gte=start_date),
                Q(payment_date__lt=end_date)
            )

        # push footer on excel
        adjustmentExcel.append(
            dict({
                'ID': "합계",
                '주문 금액': adjustment_total_price,
                '공급가액': adjustment_supply_price,
                '부가세': adjustment_surtax_price,
                '수수료': adjustment_fee,
                '정산금액': adjustment_settlement_amount,
            })
        )
    else:
        pass

    return [adjustmentList, adjustmentExcel]


def getSurtax(orderList, date_range):
    orderList = orderList.order_by('payment_date')
    surtax = {
        'sales': {},
        'purchase': {}
    }

    sales_total_price = 0
    sales_supply_price = 0
    sales_surtax_price = 0
    sales_fee = 0
    sales_settlement_amount = 0

    purchase_total_price = 0
    purchase_supply_price = 0
    purchase_surtax_price = 0

    if(orderList):
        total_price = 0
        total_order = orderList.count()

        for order in orderList:
            total_price = order.totalPrice
            supply_price = round(total_price / 1.1)
            surtax_price = total_price - supply_price
            if(order.type == ORDER_TYPE_B2B):
                fee = int(total_price * FEE_CONST)
            else:
                if(dateByTimeZone(order.payment_date) < FEE_CHANGE_DATE):
                    fee = int(total_price * FEE_CONST_BEFORE)
                else:
                    fee = int(total_price * FEE_CONST)
            settlement_amount = total_price - fee

            # all
            sales_total_price += total_price
            sales_supply_price += supply_price
            sales_surtax_price += surtax_price
            sales_fee += fee
            sales_settlement_amount += settlement_amount

            purchase_total_price += fee
            purchase_supply_price += int(fee / 1.1)
            purchase_surtax_price += fee - int(fee / 1.1)

        surtax['sales'] = dict({
            'date_range': '{} ~ {}'.format(date_range[0].strftime('%Y-%m-%d'), date_range[1].strftime('%Y-%m-%d')),
            'supply_price': '{}원'.format(format(sales_supply_price, ",")),
            'surtax_price': '{}원'.format(format(sales_surtax_price, ",")),
            'total_order': total_order,
            'total_price': '{}원'.format(format(sales_total_price, ",")),
            'unit': 'won'
        })
        surtax['purchase'] = dict({
            'date_range': '{} ~ {}'.format(date_range[0].strftime('%Y-%m-%d'), date_range[1].strftime('%Y-%m-%d')),
            'total_order': total_order,
            'supply_price': '{}원'.format(format(purchase_supply_price, ",")),
            'surtax_price': '{}원'.format(format(purchase_surtax_price, ",")),
            'total_price': '{}원'.format(format(purchase_total_price, ",")),
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
        date_range = []
        date_range.append(dateNowByTimeZone() -
                          datetime.timedelta(days=(31 * 3)))
        date_range.append(dateNowByTimeZone().replace(
            hour=23, minute=59, second=59, microsecond=0))

        orderList = Order.objects.filter(
            (
                Q(payment_date__gte=date_range[0]) &
                Q(payment_date__lt=date_range[1])
            ) &
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
                hour=23, minute=59, second=59, microsecond=0)

            if(date_range[0] > date_range[1]):
                temp = date_range[0]
                date_range[0] = date_range[1]
                date_range[1] = temp

        else:
            date_range.append(dateNowByTimeZone() -
                              datetime.timedelta(days=(31 * 3)))
            date_range.append(dateNowByTimeZone().replace(
                hour=23, minute=59, second=59, microsecond=0))

        idFilter = Q()
        if(param_valid(order_id)):
            idFilter.add(
                Q(order_id__contains=order_id.upper()), idFilter.AND)

        infoFilter = Q()
        if(param_valid(store)):
            infoFilter.add(Q(store__name__contains=store), infoFilter.AND)

        if(param_valid(menu)):
            infoFilter.add(Q(menu__name__contains=menu), infoFilter.AND)

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
            idFilter &
            infoFilter)

        total_amount = 0
        for order in orderList.filter(Q(payment_status=EATPLE_ORDER_STATUS_PAID)):
            total_amount += order.totalPrice

        response['total_amount'] = total_amount
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
                Q(payment_status=EATPLE_ORDER_STATUS_PAID)
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
                hour=23, minute=59, second=59, microsecond=0)

            if(date_range[0] > date_range[1]):
                temp = date_range[0]
                date_range[0] = date_range[1]
                date_range[1] = temp

        else:
            date_range.append(dateNowByTimeZone() -
                              datetime.timedelta(days=(31 * 3)))
            date_range.append(dateNowByTimeZone().replace(
                hour=23, minute=59, second=59, microsecond=0))

        infoFilter = Q()
        if(param_valid(store)):
            infoFilter.add(Q(store__name__contains=store), infoFilter.AND)

        orderList = orderList.filter(
            (
                Q(payment_date__gte=date_range[0]) &
                Q(payment_date__lt=date_range[1])
            ) &
            infoFilter)

        adjustmentForm = getAdjustment(orderList, date_range)
        surtax = getSurtax(orderList, date_range)

        response['adjustments'] = adjustmentForm[0]
        response['adjustments_excel'] = adjustmentForm[1]
        response['surtax'] = surtax
        response['error_code'] = 200

        return JsonResponse(response)
