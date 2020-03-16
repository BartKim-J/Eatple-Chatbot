# Django Library
from django.conf import settings

###########################################################################################
# DEBUG MODE FLAG
if(settings.SETTING_ID == 'DEPLOY'):
    pass
elif(settings.SETTING_ID == 'DEBUG'):
    pass
else:
    pass
