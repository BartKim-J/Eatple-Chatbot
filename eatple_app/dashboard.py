from django.utils.translation import ugettext_lazy as _
from jet.dashboard import modules
from jet.dashboard.dashboard import Dashboard, AppIndexDashboard

# Define
from eatple_app.define import *

from eatple_app.model.menu import Menu, PickupTime

class CustomIndexDashboard(Dashboard):
    columns = 3
            
    def init_with_context(self, context):
        menuList = Menu.objects.filter(
            store__type=STORE_TYPE_B2B,         
            status=OC_OPEN,
            store__status=OC_OPEN,
        )
        
        childrenBlock = []
        
        for menu in menuList:
            childrenBlock += {
                'title': "{store} - {menu} : {current_stock}개".format(
                    store=menu.store.name,
                    menu=menu.name,
                    current_stock=menu.current_stock,
                ),
                'url': '{host_url}/admin/eatple_app/store/{store_index}/change'.format(
                    host_url=HOST_URL,
                    store_index=menu.store.id
                ),
                'external': True,
            },
                
        self.available_children.append(modules.LinkList)
        self.children.append(modules.AppList(
            _('Stock Status'),
            children=childrenBlock,
            column=0,
            order=0
        ))
