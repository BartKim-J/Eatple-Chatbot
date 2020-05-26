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
            menuList = Menu.objects.all()
            stockTableList = StockTable.objects.all()

        except (StockTable.DoesNotExist, Menu.DoesNotExist):
            raise CommandError('Menu does not exist' % poll_id)

        for menu in menuList:
            menu.getCurrentStock()

        for stocktable in stockTableList:
            stocktable.getCurrentStock()

        self.stdout.write(self.style.SUCCESS(json.dumps(get_hw_idle_info())))
