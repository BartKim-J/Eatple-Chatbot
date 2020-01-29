# Define
from eatple_app.define import *

from django.core.management.base import BaseCommand, CommandError

# Models
from eatple_app.models import *

class Command(BaseCommand):
    help = 'Order Control Pannel'

    def add_arguments(self, parser):
    #     parser.add_argument('poll_ids', nargs='+', type=int)
        parser.add_argument(
            '--update-all',
            action='store_true',
            help='Update All Orders',
        )
        
    def handle(self, *args, **options):
        try:
            currentDate = dateNowByTimeZone()
            expireDate = currentDate + datetime.timedelta(hours=-24)
            
            print(expireDate)
            
            orderList = Order.objects.filter(
                Q(payment_date__gt=expireDate) &
                ~Q(store=None) &
                ~Q(menu=None)
            ).order_by('order_date')
            
            menuList = Menu.objects.filter(
                status=OC_OPEN,
                store__status=OC_OPEN,
            )
        except (Order.DoesNotExist, Menu.DoesNotExist):
            raise CommandError('Order or Menu does not exist' % poll_id)
        
        
        for menu in menuList:
            menu.getCurrentStock()
            
        for order in orderList:
            Order.orderStatusUpdate(order)

        self.stdout.write(self.style.SUCCESS('Successfully update order'))
