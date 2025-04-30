from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import *
from .forms import *

wizard_forms = [
    ("event", EventDetailsForm),
    ("general", GeneralInfoForm),
    ("equipment", EquipmentDetailsForm),
    ("environment", EnvironmentalConditionsForm),
    ("witness", WitnessForm),
    ("action", ActionTakenForm),
    ("followup", FollowUpForm),
]


urlpatterns = [


    path('docs', documents, name='documents'),
    path('incident-reporting', incident_reporting_system, name='incident_reporting_system'),
    path('incidents/', incident_report_list, name='incident_report_list'),
    path('incidents/<int:pk>/', incident_report_detail, name='incident_detail'),
    path('report/new/', IncidentReportWizard.as_view(wizard_forms), name='submit_incident_report'),
    path('report/success/', incident_report_success, name='incident_report_success'),
    path('report/pdf/<int:pk>/', incident_report_pdf, name='incident_report_pdf'),

    path('sops/', sop_list, name='sop_list'),
    path('sops/upload/', sop_upload, name='sop_upload'),

    path('documents/', general_document_list, name='general_document_list'),
    path('documents/upload/', upload_general_document, name='upload_general_document'),

    path('equipment/', equipment_list, name='equipment_list'),
    path('equipment/add/', equipment_create, name='equipment_create'),
    path('equipment/<int:pk>/edit/', equipment_edit, name='equipment_edit'),
    path('equipment/<int:pk>/delete/', equipment_delete, name='equipment_delete'),

    path('mission-plan', mission_plan, name='mission_plan'),
] 

if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


