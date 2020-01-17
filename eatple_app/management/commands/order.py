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
            orderList = Order.objects.all()
            
        except Order.DoesNotExist:
            raise CommandError('Order does not exist' % poll_id)
        
        for order in orderList:
            Order.orderStatusUpdate(order)

        self.stdout.write(self.style.SUCCESS('Successfully update order'))