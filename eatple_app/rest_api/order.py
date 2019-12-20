# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# Modules
from eatple_app.module_kakao.ReponseForm import *
from eatple_app.module_kakao.RequestForm import *
from eatple_app.module_kakao.Validation import *

# View-System
from eatple_app.views_system.debugger import *

from rest_framework import viewsets
from rest_framework import permissions

from eatple_app.rest_api.serializer import OrderSerializer
from eatple_app.models import Order


def eatplePassValidation(user):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()

    orderManager.availableOrderStatusUpdate()

    lunchPurchaed = orderManager.getAvailableLunchOrderPurchased().exists()
    dinnerPurchaced = orderManager.getAvailableDinnerOrderPurchased().exists()

    if (lunchPurchaed and dinnerPurchaced):
        return False

    elif (lunchPurchaed):
        return False

    elif (dinnerPurchaced):
        return False

    return True


def userValidation(user_id):
    try:
        user = User.objects.get(app_user_id=user_id)
        return user
    except User.DoesNotExist:
        return None


def orderValidation(order_id):
    try:
        order = Order.objects.get(order_id=order_id)
        return order
    except Order.DoesNotExist:
        return None

class OrderValidation(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def list(self, request, *args, **kwargs):
        buyer_name = request.query_params.get('buyer_name')
        merchant_uid = request.query_params.get('merchant_uid')

        response = {
            'order_id': merchant_uid,
            'user_id': buyer_name
        }
        
        # Account Check
        user = userValidation(buyer_name)
        if(user == False):
            response['error_code'] = 201
            response['error_msg']  = '가입되지 않은 사용자입니다. 잇플로 돌아가 다시 가입해주세요!'
            return Response(response)
        
        eatplePassStatus = eatplePassValidation(user)

        if(eatplePassStatus == False):
            response['error_code'] = 202
            response['error_msg']  = '이미 잇플패스를 발급하셨습니다.'
            return Response(response)

        try:
            order = Order.objects.get(order_id=merchant_uid)            
        except Order.DoesNotExist:
            order = None

        if(order == None):
            response['error_code'] = 203
            response['error_msg']  = '잘못된 주문번호입니다. 홈으로가서 다시 메뉴를 선택해주세요.'
            return Response(response)            
        else:
            order.orderStatusUpdate()
            
        if(order.payment_status == IAMPORT_ORDER_STATUS_PAID):
            response['error_code'] = 204
            response['error_msg']  = '이미 결제가 완료된 주문번호 입니다.'
            return Response(response)
        
        elif(order.payment_status == IAMPORT_ORDER_STATUS_CANCELLED):
            response['error_code'] = 205
            response['error_msg'] = '이미 환불이 완료된 주문번호 입니다.'
            return Response(response)
        
        # Store Check
        if(order.store.status != OC_OPEN or order.menu.status != OC_OPEN):
            response['error_code'] = 206
            response['error_msg'] = '현재 주문 가능시간이 아닙니다. 상점 메뉴를 새로고침한 다음 사용해주세요.'
            return Response(response)
        
        # Time Check
        
        currentSellingTime = sellingTimeCheck()
        isClosedDay = weekendTimeCheck()
        
        if(currentSellingTime != order.menu.selling_time or isClosedDay == True):
            response['error_code'] = 206
            response['error_msg'] = '현재 주문 가능시간이 아닙니다. 상점 메뉴를 새로고침한 다음 사용해주세요.'
            return Response(response)
        
        
        response['error_code'] = 200
        response['error_msg'] = '정상적인 주문입니다. 결제로 넘어갑니다.'
        return Response(response)