# System
import os
import sys

# Django Library
from django.conf import settings
from django.utils import timezone

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
from eatple_app.system.timeSheet import *
from eatple_app.system.slack import *
from eatple_app.system.kakao import *
from eatple_app.system.iamport import *

###########################################################################################
# System Variable

VERSION_CODE = "동그랑땡"
VERSION_LEVEL = "Beta"
MAJOR_VERSION = 1
MINOR_VERSION = 0
BUILD_VERSION = 5
