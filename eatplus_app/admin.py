'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
from django.contrib import admin

from .models_store import DefaultImage
from .models_store import Store, Menu 
from .models_store import Category, SubCategory
from .models_order import Order
from .models_user  import User


admin.site.register(User)

admin.site.register(Order)

admin.site.register(Category)
admin.site.register(SubCategory)

admin.site.register(Store)
admin.site.register(Menu)

admin.site.register(DefaultImage)
