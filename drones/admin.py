from django.contrib import admin
from .models import *
from .forms import EquipmentForm

@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    form = EquipmentForm

admin.site.register(DroneIncidentReport)
admin.site.register(SOPDocument)
admin.site.register(GeneralDocument)