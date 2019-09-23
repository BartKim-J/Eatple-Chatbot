'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
#Django Library
from django.contrib import admin

#Models
from .models import DefaultImage
from .models import Store, Menu 
from .models import Category, SubCategory
from .models import Order
from .models import User


#Main Models
admin.site.register(User)
admin.site.register(Store)
admin.site.register(Menu)

#Defulat Images
admin.site.register(DefaultImage)

#Order
admin.site.register(Order)

#Menu Category-SubCategory
admin.site.register(Category)
admin.site.register(SubCategory)


