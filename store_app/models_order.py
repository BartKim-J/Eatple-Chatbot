from django.urls import reverse
from django.db import models
from django_mysql.models import Model

import datetime

from .models_store import Store, Menu
from .models_config import Config

class Order(models.Model):
    class Meta:
        ordering = ['-order_date']

    menu_id          = models.ForeignKey(Menu,  on_delete=models.DO_NOTHING, default=Config.DEFAULT_OBJECT_ID)

    management_code  = models.CharField(max_length=Config.MANAGEMENT_CODE_LENGTH, blank=True, null=True,
                                        help_text="Menu Magement Code")

    order_date       = models.DateTimeField(auto_now=True)

    status           = models.CharField(max_length=Config.STRING_LENGTH, choices=Config.ORDER_STATUS, default=Config.ORDER_STATUS[0])

    def make_order(self):
        return self.management_code

            # Methods
    def __str__(self):
        return "{} - {}".format(self.status, self.order_date)
