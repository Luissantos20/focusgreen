from django.contrib import admin
from .models import ScreenTimeEntry

@admin.register(ScreenTimeEntry)
class ScreenTimeEntryAdmin(admin.ModelAdmin):
    list_display = ('user', 'minutes', 'category', 'started_at')
    list_filter = ('category', 'started_at')

