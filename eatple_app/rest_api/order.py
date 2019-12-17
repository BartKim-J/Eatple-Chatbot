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

# View-System
from eatple_app.views_system.debugger import *

from rest_framework import viewsets
from rest_framework import permissions

from eatple_app.rest_api.serializer import OrderSerializer
from eatple_app.models import Order


def eatplePassValidation(user):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()
    
    orderManager.availableOrderStatusUpdate();

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
    
    def get_queryset(self):
        storeName = self.request.query_params.get('storeName')
        menuName= self.request.query_params.get('menuName')
        menuPrice = self.request.query_params.get('menuPrice')
        buyer_name = self.request.query_params.get('buyer_name')
        buyer_tel = self.request.query_params.get('buyer_tel')
        buyer_email = self.request.query_params.get('buyer_email')
        merchant_uid = self.request.query_params.get('merchant_uid')

        user = userValidation(buyer_name)
        ret = eatplePassValidation(user)
        
        if(ret == False):
            return None;
        
        order = self.queryset.filter(order_id=merchant_uid)[:1]
        
        retQueryset = order
        
        return retQueryset
        
