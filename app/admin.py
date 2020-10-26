# -*- encoding: utf-8 -*-
"""
License: MIT
Copyright (c) 2019 - present AppSeed.us
"""

from django.contrib import admin
from .models import Sample
from simple_history.admin import SimpleHistoryAdmin
# Register your models here.

admin.site.register(Sample, SimpleHistoryAdmin)