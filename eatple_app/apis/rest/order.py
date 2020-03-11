# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.responseForm import *
from eatple_app.module_kakao.requestForm import *
from eatple_app.module_kakao.kakaoPay import *
from eatple_app.module_kakao.validation import *

from eatple_app.apis.rest.validation import *

# View-System
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.error_table import *

from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions

from eatple_app.apis.rest.serializer import OrderSerializer


class OrderValidation(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get']

    @swagger_auto_schema(
        operation_description="주문 증명",
        responses={
            200:
                ORDER_200_VALID.as_md(),
            400:
                ORDER_201_USER_INVALID.as_md() +
                ORDER_202_MULTI_ORDER.as_md() +
                ORDER_203_ORDER_ID_INVALID.as_md() +
                ORDER_204_ALREADY_PAID.as_md() +
                ORDER_205_ALREADY_CANCELLED.as_md() +
                ORDER_206_SELLING_TIME_INVALID.as_md()
        }
    )
    def list(self, request, *args, **kwargs):
        buyer_name = request.query_params.get('buyer_name')
        merchant_uid = request.query_params.get('merchant_uid')

        response = {
            'order_id': merchant_uid,
        }

        if(merchant_uid == None):
            response['error_code'] = PARAM_600_MERCHANT_UID_INVALID.code
            response['error_msg'] = PARAM_600_MERCHANT_UID_INVALID.message

            return Response(response, status=PARAM_600_MERCHANT_UID_INVALID.status)

        # Order Check
        order = orderValidation(merchant_uid)

        if(order == None or order.payment_status == EATPLE_ORDER_STATUS_FAILED):
            response['error_code'] = ORDER_203_ORDER_ID_INVALID.code
            response['error_msg'] = ORDER_203_ORDER_ID_INVALID.message
            return Response(response)
        elif(order.payment_status == EATPLE_ORDER_STATUS_PAID):
            response['error_code'] = ORDER_100_SUCCESS.code
            response['error_msg'] = ORDER_100_SUCCESS.message
            return Response(response)
        elif(order.payment_status == EATPLE_ORDER_STATUS_CANCELLED):
            response['error_code'] = ORDER_205_ALREADY_CANCELLED.code
            response['error_msg'] = ORDER_205_ALREADY_CANCELLED.message
            return Response(response)
        else:
            # Order Payment Type Setup to INI Pay
            order.payment_type = ORDER_PAYMENT_INI_PAY
            order.save()

            beforeOrderStatus = order.payment_status
            order.orderStatusUpdate()

            if(beforeOrderStatus != EATPLE_ORDER_STATUS_PAID and
               order.payment_status == EATPLE_ORDER_STATUS_PAID):
                order.payment_date = dateNowByTimeZone()
                order.save()

                response['error_code'] = ORDER_100_SUCCESS.code
                response['error_msg'] = ORDER_100_SUCCESS.message
                return Response(response)

        # Account Check
        user = userValidation(order.ordersheet.user.app_user_id)
        if(user == None):
            response['error_code'] = ORDER_201_USER_INVALID.code
            response['error_msg'] = ORDER_201_USER_INVALID.message
            return Response(response)

        # Eatple Pass Check
        eatplePassStatus = eatplePassValidation(user)
        if(eatplePassStatus == False):
            response['error_code'] = ORDER_202_MULTI_ORDER.code
            response['error_msg'] = ORDER_202_MULTI_ORDER.message
            return Response(response)

        # Time Check
        currentSellingTime = sellingTimeCheck()
        isClosedDay = weekendTimeCheck()

        if(currentSellingTime != order.menu.selling_time or isClosedDay == True):
            response['error_code'] = ORDER_206_SELLING_TIME_INVALID.code
            response['error_msg'] = ORDER_206_SELLING_TIME_INVALID.message
            return Response(response)

        # Store Check
        if(order.store.status != OC_OPEN or order.menu.status != OC_OPEN):
            response['error_code'] = ORDER_206_SELLING_TIME_INVALID.code
            response['error_msg'] = ORDER_206_SELLING_TIME_INVALID.message
            return Response(response)

        response['error_code'] = ORDER_200_VALID.code
        response['error_msg'] = ORDER_200_VALID.message
        return Response(response)


class OrderInformation(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ['get']

    def list(self, request, *args, **kwargs):
        buyer_name = request.query_params.get('buyer_name')
        merchant_uid = request.query_params.get('merchant_uid')

        response = {
            'order_id': merchant_uid,
        }

        if(merchant_uid == None):
            response['error_code'] = PARAM_600_MERCHANT_UID_INVALID.code
            response['error_msg'] = PARAM_600_MERCHANT_UID_INVALID.message

            return Response(response, status=PARAM_600_MERCHANT_UID_INVALID.status)

        # Order Check
        order = orderValidation(merchant_uid)

        if(order == None or order.payment_status == EATPLE_ORDER_STATUS_FAILED):
            response['error_code'] = ORDER_203_ORDER_ID_INVALID.code
            response['error_msg'] = ORDER_203_ORDER_ID_INVALID.message
            return Response(response)

        if(order.payment_status == EATPLE_ORDER_STATUS_PAID):
            response['error_code'] = ORDER_204_ALREADY_PAID.code
            response['error_msg'] = ORDER_204_ALREADY_PAID.message
            return Response(response)

        if(order.payment_status == EATPLE_ORDER_STATUS_CANCELLED):
            response['error_code'] = ORDER_205_ALREADY_CANCELLED.code
            response['error_msg'] = ORDER_205_ALREADY_CANCELLED.message
            return Response(response)

        # Account Check
        user = userValidation(order.ordersheet.user.app_user_id)
        if(user == None):
            response['error_code'] = ORDER_201_USER_INVALID.code
            response['error_msg'] = ORDER_201_USER_INVALID.message
            return Response(response)

        response['store'] = order.store.name
        response['menu'] = order.menu.name
        response['amount'] = order.totalPrice
        response['buyer_email'] = user.email
        response['buyer_tel'] = user.phone_number.as_national
        response['buyer_name'] = user.nickname

        return Response(response)
