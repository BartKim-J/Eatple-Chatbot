from django.shortcuts import render

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# TEMPLATES
def stock_list(request):
    menus = Menu.objects.filter(status=OC_OPEN)
    
    return render(request, 'eatple_app/stock_list.html', {'menus': menus})
