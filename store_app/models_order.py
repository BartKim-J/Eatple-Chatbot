#Django Library
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

#External Library
import datetime

#Models 
from .models_config import Config

class Order(models.Model):
    class Meta:
        ordering = ['-order_date']

    userInstance     = models.ForeignKey('User',  on_delete=models.DO_NOTHING, default=Config.DEFAULT_OBJECT_ID)
    storeInstance    = models.ForeignKey('Store',  on_delete=models.DO_NOTHING, default=Config.DEFAULT_OBJECT_ID)
    menuInstance     = models.ForeignKey('Menu',  on_delete=models.DO_NOTHING, default=Config.DEFAULT_OBJECT_ID)

    management_code  = models.CharField(max_length=Config.MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                        help_text="Menu Magement Code")

    update_date      = models.DateTimeField(auto_now_add=False, auto_now=True)
    order_date       = models.DateTimeField(auto_now_add=True,  auto_now=False)

    status           = models.CharField(max_length=Config.STRING_LENGTH, choices=Config.ORDER_STATUS, default=Config.ORDER_STATUS[0][0])

    @classmethod
    def pushOrder(cls, userInstance, storeInstance, menuInstance):
        management_code = Config.MANAGEMENT_CODE_DEFAULT
        order_date       = models.DateTimeField(auto_now=True)

        pushedOrder = cls(userInstance=userInstance, storeInstance=storeInstance, menuInstance=menuInstance, management_code=management_code, order_date=order_date)
        pushedOrder.save()

        return pushedOrder

    # Methods
    def __str__(self):
        return "{} - {} :: {}".format(self.management_code, self.status, self.order_date)
