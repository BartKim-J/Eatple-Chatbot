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
            storeList = Store.objects.all()

        except (Store.DoesNotExist):
            raise CommandError('Store does not exist' % poll_id)

        orderTimeSheet = OrderTimeSheet()
        currentDate = orderTimeSheet.GetCurrentDate()

        hour = currentDate.hour
        min = currentDate.min

        # Check Order Flag To False
        # 2:00 PM and AM 9:00 PM
        if((hour == 14 and min == 0) or (hour == 21 and min == 0)):
            for store in storeList:
                store.is_check_order == False

        self.stdout.write(self.style.SUCCESS(json.dumps(get_hw_idle_info())))
