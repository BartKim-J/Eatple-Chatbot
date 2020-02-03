from django.shortcuts import render

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# TEMPLATES
def base(request):
    menus = Menu.objects.order_by('-current_stock','store__name')
    
    return render(request, 'base/index.html', {'menus': menus})
