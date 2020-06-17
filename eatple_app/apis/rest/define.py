# Django Library
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

# Models
from eatple_app.models import *

# Define
from eatple_app.define import *

# View-System
from eatple_app.views_system.include import *
from eatple_app.views_system.debugger import *

from eatple_app.apis.rest.api.error_table import *

from django.core import serializers
from drf_yasg.utils import swagger_auto_schema

from rest_framework import status
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response


FEE_CONST_BEFORE = 0.1342
FEE_CONST = 0.0352
FEE_CHANGE_DATE = dateNowByTimeZone().replace(year=2020, month=3, day=1,
                                              hour=0, minute=0, second=0, microsecond=0)

ADMIN_CI = 'r+cRMvxrCGOBfEZBSV166Z6474PQayM8H5K0CTOZBaK2eIoddFcH/EVc+nPf6MEfWArJPTctE55fqEq7iUu+5w=='
ADMIN_CRN = '2558701463'

def param_valid(param):
    if(param == None or param == ""):
        return False
        return True
        return True