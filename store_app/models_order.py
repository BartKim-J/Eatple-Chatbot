#Django Library
from django.urls import reverse
from django.db import models
from django_mysql.models import Model

#External Library
from datetime import datetime, timedelta

#Models 
from .models_config import Config

#GLOBAL CONFIG
NOT_APPLICABLE          = Config.NOT_APPLICABLE
DEFAULT_OBJECT_ID       = Config.DEFAULT_OBJECT_ID

ORDER_STATUS_DICT       = Config.ORDER_STATUS_DICT
ORDER_STATUS            = Config.ORDER_STATUS

MANAGEMENT_CODE_LENGTH  = Config.MANAGEMENT_CODE_LENGTH
STRING_LENGTH           = Config.STRING_LENGTH

MANAGEMENT_CODE_DEFAULT = Config.MANAGEMENT_CODE_DEFAULT


def OrderManagementCodeGenerator(storeInstance, menuInstance, userInstance, order_date):
    management_code = ''
    management_code += '{:02d}'.format(storeInstance.id % 10)
    management_code += '{:02d}'.format(menuInstance.id % 10)
    management_code += '{:02d}'.format(userInstance.id % 10)
    management_code += order_date.strftime("%M%H%S")

    return management_code

#STATIC CONFIG
class Order(models.Model):
    class Meta:
        ordering = ['-order_date']

    userInstance     = models.ForeignKey('User',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    storeInstance    = models.ForeignKey('Store',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)
    menuInstance     = models.ForeignKey('Menu',  on_delete=models.DO_NOTHING, default=DEFAULT_OBJECT_ID)

    management_code  = models.CharField(max_length=MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                        help_text="Menu Magement Code")

    pickupTime       = models.DateTimeField(default=datetime.now())

    update_date      = models.DateTimeField(auto_now_add=False, auto_now=True)
    order_date       = models.DateTimeField(default=datetime.now())

    status           = models.CharField(max_length=STRING_LENGTH, choices=ORDER_STATUS, default=ORDER_STATUS[ORDER_STATUS_DICT['주문 완료']][0])

    @classmethod
    def pushOrder(cls, userInstance, storeInstance, menuInstance, pickupTime):
        order_date       = datetime.now()
        pickupTime       = cls.localePickupTimeToDatetime(pickupTime)
        management_code  = OrderManagementCodeGenerator(storeInstance, menuInstance, userInstance, datetime.now())

        pushedOrder = cls(userInstance=userInstance, storeInstance=storeInstance, menuInstance=menuInstance, management_code=management_code, pickupTime=pickupTime, order_date=order_date)
        pushedOrder.save()

        return pushedOrder
    
    def localePickupTimeToDatetime(pickupTime):
        return datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(hours=int(pickupTime[0:2]), minutes=int(pickupTime[3:5]))

    # Methods
    def __str__(self):
        return "{} - {} :: {}".format(self.management_code, self.status, self.order_date)
