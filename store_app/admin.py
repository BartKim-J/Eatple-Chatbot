from django.contrib import admin

from .models_store import Store, Menu 
from .models_store import Category, SubCategory
from .models_order import Order

admin.site.register(Order)

admin.site.register(Category)
admin.site.register(SubCategory)

admin.site.register(Store)
admin.site.register(Menu)
