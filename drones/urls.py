from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from .views import (
    # Incident Reporting
    documents,
    incident_reporting_system,
    incident_report_list,
    incident_report_detail,
    IncidentReportWizard,
    incident_report_success,
    incident_report_pdf,

    # SOPs and Documents
    sop_list,
    sop_upload,
    general_document_list,
    upload_general_document,

    # Equipment
    equipment_list,
    equipment_create,
    equipment_edit,
    equipment_delete,
    equipment_pdf,
    equipment_pdf_single,

    # Drones
    drone_portal,

    # Flight Logs
    flightlog_list,
    flightlog_detail,
    upload_flightlog_csv,
    flightlog_edit,
    flightlog_delete,
    flightlog_pdf,
    export_flightlogs_csv,
)

from .forms import (
    EventDetailsForm,
    GeneralInfoForm,
    EquipmentDetailsForm,
    EnvironmentalConditionsForm,
    WitnessForm,
    ActionTakenForm,
    FollowUpForm,
)

# Incident report wizard steps
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
    # Incident Reporting
    path('docs', documents, name='documents'),
    path('drone-portal/', drone_portal, name='drone_portal'),
    
    path('incident-reporting', incident_reporting_system, name='incident_reporting_system'),
    path('incidents/', incident_report_list, name='incident_report_list'),
    path('incidents/<int:pk>/', incident_report_detail, name='incident_detail'),
    path('report/new/', IncidentReportWizard.as_view(wizard_forms), name='submit_incident_report'),
    path('report/success/', incident_report_success, name='incident_report_success'),
    path('report/pdf/<int:pk>/', incident_report_pdf, name='incident_report_pdf'),

    # SOPs and General Documents
    path('sops/', sop_list, name='sop_list'),
    path('sops/upload/', sop_upload, name='sop_upload'),
    path('documents/', general_document_list, name='general_document_list'),
    path('documents/upload/', upload_general_document, name='upload_general_document'),

    # Equipment
    path('equipment/', equipment_list, name='equipment_list'),
    path('equipment/create/', equipment_create, name='equipment_create'),
    path('equipment/pdf/', equipment_pdf, name='equipment_pdf'),
    path('equipment/<uuid:pk>/edit/', equipment_edit, name='equipment_edit'),
    path('equipment/<uuid:pk>/delete/', equipment_delete, name='equipment_delete'),
    path('equipment/<uuid:pk>/pdf/', equipment_pdf_single, name='equipment_pdf_single'),


    # Flight Logs
    path('flightlogs/', flightlog_list, name='flightlog_list'),
    path('flight-upload/', upload_flightlog_csv, name='flightlog_upload'),
    path('flightlogs/<int:pk>/', flightlog_detail, name='flightlog_detail'),
    path('flightlogs/<int:pk>/edit/', flightlog_edit, name='flightlog_edit'),
    path('flightlogs/<int:pk>/delete/', flightlog_delete, name='flightlog_delete'),
    path('flightlogs/<int:pk>/pdf/', flightlog_pdf, name='flightlog_pdf'),
    path('flightlogs/export/csv/', export_flightlogs_csv, name='export_flightlogs_csv'),
]


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
