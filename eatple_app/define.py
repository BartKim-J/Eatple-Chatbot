# System
import os
import sys

# Django Library
from django.conf import settings
from django.utils import timezone

# External Library
import datetime

import requests
import json

###########################################################################################
# System
from eatple_app.system.db import *
from eatple_app.system.admin import *
from eatple_app.system.rest_framework import *

from eatple_app.system.mode import *
from eatple_app.system.urls import *
from eatple_app.system.model_type import *
from eatple_app.system.timetable import *
from eatple_app.system.slack import *
from eatple_app.system.kakao import *
from eatple_app.system.iamport import *

###########################################################################################
# Default Value
# Location

LOCATION_DEFAULT_ADDR = '강남 사거리'
LOCATION_DEFAULT_LAT = 37.497907
LOCATION_DEFAULT_LNG = 127.027635
