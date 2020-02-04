from django.shortcuts import render

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# TEMPLATES
def base(request):
    menus = Menu.objects.filter(~Q(store__type=STORE_TYPE_EVENT)).order_by('-status', '-store__status', '-current_stock','store__name')
    
    totalStock = 0
    for menu in  Menu.objects.filter(~Q(current_stock=0)):
        totalStock += menu.current_stock
    
    totalUser = User.objects.all().count()
    totalOrder = Order.objects.filter(Q(payment_status=IAMPORT_ORDER_STATUS_PAID)).count()
    
    return render(request, 'base/index.html', {
        'menus': menus,
        'totalStock': totalStock,
        'totalPrice': totalStock * 6000,
        'totalUser': totalUser,
        'totalOrder': totalOrder,
    })
