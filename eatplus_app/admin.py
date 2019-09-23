'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
from django.contrib import admin

from .models import DefaultImage
from .models import Store, Menu 
from .models import Category, SubCategory
from .models import Order
from .models import User


admin.site.register(User)

admin.site.register(Order)

admin.site.register(Category)
admin.site.register(SubCategory)

admin.site.register(Store)
admin.site.register(Menu)

admin.site.register(DefaultImage)
