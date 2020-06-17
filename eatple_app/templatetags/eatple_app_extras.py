# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

from django import template

register = template.Library()

@register.filter
def div(value, div):
    if div == 0:
        div = 1

    return round((value / div) * 100, 2)

@register.filter
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')

@register.filter
def lower(value): # Only one argument.
    """Converts a string into all lowercase"""
    return value.lower()

@register.filter
def totalStock(value):
    totalStock = 0

    menuList = Menu.objects.filter(store__id=value)
    
    for menu in menuList:
        totalStock += menu.current_stock

    return totalStock

@register.filter
def storeType(value):
    store = Store.objects.get(id=value)

    return dict(STORE_TYPE)[store.type]

@register.filter
def storePhoneNumber(value):
    store = Store.objects.get(id=value)

    if(store.phone_number != None):
        return store.phone_number.as_national 
    else:
        return "미등록"