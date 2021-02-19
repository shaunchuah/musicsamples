from django.contrib import admin
from .models import Sample, Note
from simple_history.admin import SimpleHistoryAdmin

admin.site.register(Sample, SimpleHistoryAdmin)
admin.site.register(Note, SimpleHistoryAdmin)