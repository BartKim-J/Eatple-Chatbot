'''
    Author : Ben Kim

    @NOTE
    @BUG
    @TODO
 
'''
# Django Library
from django.contrib import admin

# Models
from .models import DefaultImage
from .models import UserManual, PartnerManual
from .models import UserIntro, PartnerIntro
from .models import Store, Menu
from .models import Category, Tag
from .models import Order, OrderBox
from .models import User
from .models import Partner

# Main Models
admin.site.register(Partner)
admin.site.register(User)

admin.site.register(Store)
admin.site.register(Menu)

# Defulat Images
admin.site.register(DefaultImage)

# Order
admin.site.register(OrderBox)
admin.site.register(Order)

# Menu Category-Tag
admin.site.register(Category)
admin.site.register(Tag)

# Manual
admin.site.register(UserManual)
admin.site.register(PartnerManual)

# Intro
admin.site.register(UserIntro)
admin.site.register(PartnerIntro)
