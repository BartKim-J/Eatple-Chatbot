# Define
from eatple_app.define import *
from eatple_app.management.commands.utils import *

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
            orderTimeSheet = OrderTimeSheet()
            currentDate = orderTimeSheet.GetCurrentDate()
            expireDate = orderTimeSheet.GetOrderExpireDate()

            orderList = Order.objects.filter(
                Q(payment_date__gte=expireDate) &
                ~Q(store=None) &
                ~Q(menu=None) &
                Q(payment_status=EATPLE_ORDER_STATUS_PAID)
            ).order_by('order_date')

        except (Order.DoesNotExist):
            raise CommandError('Order does not exist' % poll_id)

        for order in orderList:
            Order.orderStatusUpdate(order)

        self.stdout.write(self.style.SUCCESS(json.dumps(get_hw_idle_info())))
