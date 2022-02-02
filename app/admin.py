from django.contrib import admin
from .models import Sample
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Sample, SimpleHistoryAdmin)