# System
import os
import sys

# Django Library
from django.conf import settings
from django.utils import timezone

import requests
import json
import urllib.parse

###########################################################################################
# System
from sales_app.system.db import *
from sales_app.system.admin import *
from sales_app.system.rest_framework import *

from sales_app.system.mode import *
from sales_app.system.urls import *
from sales_app.system.model_type import *

###########################################################################################
# System Variable

VERSION_CODE = "동그랑땡"
VERSION_LEVEL = "Beta"
MAJOR_VERSION = 1
MINOR_VERSION = 0
BUILD_VERSION = 0
