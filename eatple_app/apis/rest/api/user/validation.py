# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *


def eatplePassValidation(user):
    orderManager = UserOrderManager(user)
    orderManager.orderPaidCheck()

    orderManager.availableOrderStatusUpdate()

    lunchPurchaed = orderManager.getAvailableLunchOrder().exists()
    dinnerPurchaced = orderManager.getAvailableDinnerOrder().exists()

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
