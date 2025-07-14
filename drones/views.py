from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from formtools.wizard.views import SessionWizardView
from django.template.loader import render_to_string
from django.template.loader import get_template
from django.templatetags.static import static
from django.core.paginator import Paginator
from datetime import datetime, timedelta
from django.utils.timezone import now
from django.http import HttpResponse
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from datetime import timedelta
from weasyprint import HTML 
import os
import csv
import uuid
import tempfile
import re
from .forms import *
from .models import *
from datetime import timedelta



@login_required
def drone_portal(request):

    total_flights = FlightLog.objects.count()
    active_drones = FlightLog.objects.all()
    total_flight_time = timedelta()
    total_photos = 0
    total_videos = 0

    all_logs = FlightLog.objects.all()
    for log in all_logs:
        if log.air_time:
            total_flight_time += log.air_time
        if log.photos:
            total_photos += log.photos
        if log.videos:
            total_videos += log.videos

    active_drones = (
        FlightLog.objects.exclude(drone_serial='')
        .values_list('drone_serial', flat=True)
        .distinct()
        .count()
    )

    context = {

        'active_drones': active_drones,
        'total_flights': total_flights,
        'total_flight_time': total_flight_time,
        'total_photos': total_photos,
        'total_videos': total_videos,
        'current_page': 'home'
    }

    return render(request, 'drones/drone_portal.html', context)





# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- Documents Views


@login_required
def documents(request):
    context = {'current_page': 'document'}  
    return render(request, 'drones/drone_portal.html', context)


@login_required
def incident_reporting_system(request):
    query = request.GET.get('q', '').strip()
    reports = DroneIncidentReport.objects.all().order_by('-report_date')
    if query:
        reports = reports.filter(
            Q(reported_by__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )
    context = {
        'incident_reports': reports,
        'search_query': query,
        'current_page': 'incidents' 
        
    }
    return render(request, 'drones/incident_reporting_system.html', context)


@login_required
def incident_report_pdf(request, pk):
    report = get_object_or_404(DroneIncidentReport, pk=pk)
    logo_path = request.build_absolute_uri(static("images/logo2.png"))
    context = {
        'report': report,
        'logo_path': logo_path,
        'now': timezone.now(),
        'current_page': 'incidents' 
        
    }
    html_string = render_to_string('drones/incident_report_pdf.html', context, request=request)
    html = HTML(string=html_string, base_url=request.build_absolute_uri())
    pdf_content = html.write_pdf()
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="incident_report_{pk}.pdf"'
    response.write(pdf_content)
    return response

FORMS = [
    ("general", GeneralInfoForm),
    ("event", EventDetailsForm),
    ("equipment", EquipmentDetailsForm),
    ("environment", EnvironmentalConditionsForm),
    ("witness", WitnessForm),
    ("action", ActionTakenForm),
    ("followup", FollowUpForm),
]

TEMPLATES = {
    "general": "drones/wizard_form.html",
    "event": "drones/wizard_form.html",
    "equipment": "drones/wizard_form.html",
    "environment": "drones/wizard_form.html",
    "witness": "drones/wizard_form.html",
    "action": "drones/wizard_form.html",
    "followup": "drones/wizard_form.html",
}

class IncidentReportWizard(SessionWizardView, LoginRequiredMixin):
    template_name = 'drones/incident_report_form.html'

    def get(self, request, *args, **kwargs):
        self.storage.reset()
        return super().get(request, *args, **kwargs)

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        current_step = self.steps.step1 + 1
        total_steps = self.steps.count
        progress_percent = int((current_step / total_steps) * 100)
        context.update({
            'current_step': current_step,
            'total_steps': total_steps,
            'progress_percent': progress_percent,
            'current_page': 'incidents' 
            
        })
        return context

    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)
        report = DroneIncidentReport.objects.create(**data)
        context = {'report': report, 'current_page': 'incidents'} 
        
        html_string = render_to_string('drones/incident_report_pdf.html', context, request=self.request)
        html = HTML(string=html_string, base_url=self.request.build_absolute_uri())
        pdf_content = html.write_pdf()
        unique_id = uuid.uuid4()
        filename = f'reports/incident_report_{report.pk}_{unique_id}.pdf'
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            f.write(pdf_content)
        pdf_url = os.path.join(settings.MEDIA_URL, filename)
        context = {
            'form_data': data,
            'pdf_url': pdf_url,
            'current_page': 'incidents' 
            
        }
        return render(self.request, 'drones/incident_report_success.html', context)


@login_required
def incident_report_success(request):
    pdf_url = request.GET.get('pdf_url', None)
    context = {'pdf_url': pdf_url, 'current_page': 'incidents'} 
    
    return render(request, 'drones/report_success.html', context)


@login_required
def incident_report_list(request):
    query = request.GET.get('q', '')
    reports = DroneIncidentReport.objects.all()
    if query:
        reports = reports.filter(
            Q(reported_by__icontains=query) |
            Q(location__icontains=query) |
            Q(description__icontains=query)
        )
    context = {
        'incident_reports': reports.order_by('-report_date'),
        'search_query': query,
        'current_page': 'incidents' 
        
    }
    return render(request, 'drones/incident_list.html', context)


@login_required
def incident_report_detail(request, pk):
    report = get_object_or_404(DroneIncidentReport, pk=pk)
    context = {'report': report, 'current_page': 'incidents'} 
    
    return render(request, 'drones/incident_report_detail.html', context)


@login_required
def sop_upload(request):
    if request.method == 'POST':
        form = SOPDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "SOP added successfully.")
            return redirect('sop_list')
        else:
            messages.error(request, "There was a problem uploading the document.")
    else:
        form = SOPDocumentForm()
    context = {'form': form, 'current_page': 'sop'} 
    return render(request, 'sop_manager/sop_upload.html', context)


@login_required
def sop_list(request):
    sops = SOPDocument.objects.order_by('-created_at')
    paginator = Paginator(sops, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'sops': page_obj,
        'page_obj': page_obj,
        'current_page': 'sop' 
    }
    return render(request, 'sop_manager/sop_list.html', context)


@login_required
def general_document_list(request):
    search_query = request.GET.get('q', '').strip()
    selected_category = request.GET.get('category', '')
    documents = GeneralDocument.objects.all().order_by('-uploaded_at')
    if search_query:
        documents = documents.filter(title__icontains=search_query)
    if selected_category:
        documents = documents.filter(category=selected_category)
    categories = GeneralDocument.objects.values_list('category', flat=True).distinct()
    paginator = Paginator(documents, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'documents': page_obj,
        'page_obj': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'current_page': 'documents'  
    }
    return render(request, 'drones/general_list.html', context)


@login_required
def upload_general_document(request):
    if request.method == 'POST':
        form = GeneralDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "File added successfully.")
            return redirect('general_document_list')
        else:
            messages.error(request, "There was a problem uploading the document.")
    else:
        form = GeneralDocumentForm()
    context = {'form': form, 'current_page': 'document'}  
    return render(request, 'drones/upload_general.html', context)

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- EQUIPMENT Views


@login_required
def equipment_list(request):
    equipment = Equipment.objects.all().order_by('-purchase_date', 'name')

    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm()

    context = {
        'equipment': equipment,
        'form': form,
        'current_page': 'equipment',
    }
    return render(request, 'drones/equipment_list.html', context)



def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'equipment_list.html', {'form': form})


@login_required
def equipment_edit(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, request.FILES, instance=item) 
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=item)

    return render(request, 'drones/equipment_edit.html', {
        'form': form,
        'item': item
    })


@login_required
def equipment_delete(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        equipment.delete()
        messages.success(request, f'Equipment "{equipment.name}" deleted.')
        return redirect('equipment_list')
    return render(request, 'drones/equipment_confirm_delete.html', {
        'equipment': equipment,
        'current_page': 'equipment'
    })


@login_required
def equipment_pdf(request):
    equipment = Equipment.objects.all().order_by('equipment_type', 'name')
    template = get_template('drones/equipment_pdf.html')
    html_string = template.render({'equipment': equipment})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename=equipment_inventory.pdf'

    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        HTML(string=html_string).write_pdf(target=tmp_file.name)
        tmp_file.seek(0)
        response.write(tmp_file.read())

    return response




@login_required
def equipment_pdf_single(request, pk):
    equipment = get_object_or_404(Equipment, pk=pk)
    logo_url = request.build_absolute_uri(static('images/logo2.png'))
    
    template = get_template('drones/equipment_pdf_single.html')
    html_string = template.render({'item': equipment, 'logo_url': logo_url})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename={equipment.name}_equipment.pdf'

    with tempfile.NamedTemporaryFile(delete=True) as tmp_file:
        HTML(string=html_string).write_pdf(target=tmp_file.name)
        tmp_file.seek(0)
        response.write(tmp_file.read())

    return response


# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=- FlightLog Views


@login_required
def flightlog_list(request):
    log_list = FlightLog.objects.all().order_by('-flight_date')
    paginator = Paginator(log_list, 50)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'logs': page_obj, 'current_page': 'flightlogs'}  
    return render(request, 'drones/flightlog_list.html', context)


@login_required
def export_flightlogs_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="flight_logs.csv"'

    writer = csv.writer(response)
    fields = [field.name for field in FlightLog._meta.fields]
    writer.writerow(fields)

    for log in FlightLog.objects.all().order_by('-flight_date'):
        row = [getattr(log, field) for field in fields]
        writer.writerow(row)

    return response

@login_required
def flightlog_detail(request, pk):
    log = get_object_or_404(FlightLog, pk=pk)
    context = {'log': log, 'current_page': 'flightlogs'}  
    return render(request, 'drones/flightlog_detail.html', context)


@login_required
def flightlog_edit(request, pk):
    log = get_object_or_404(FlightLog, pk=pk)
    if request.method == 'POST':
        form = FlightLogCSVUploadForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            return redirect('flightlog_list')
    else:
        form = FlightLogCSVUploadForm(instance=log)
    context = {'form': form, 'log': log, 'current_page': 'flightlogs'}  
    return render(request, 'drones/flightlog_form.html', context)


@login_required
def flightlog_business(request, pk):
    log = get_object_or_404(FlightLog, pk=pk)
    if request.method == 'POST':
        form = FlightLogCSVUploadForm(request.POST, instance=log)
        if form.is_valid():
            form.save()
            return redirect('flightlog_list')
    else:
        form = FlightLogCSVUploadForm(instance=log)
    context = {'form': form, 'log': log, 'current_page': 'flightlogs'}  
    return render(request, 'drones/flightlog_form.html', context)


@login_required
def flightlog_delete(request, pk):
    log = get_object_or_404(FlightLog, pk=pk)
    if request.method == 'POST':
        log.delete()
        return redirect('flightlog_list')
    context = {'log': log, 'current_page': 'flightlogs'}  
    return render(request, 'drones/flightlog_confirm_delete.html', context)


@login_required
def flightlog_pdf(request, pk):
    log = get_object_or_404(FlightLog, pk=pk)
    context = {'log': log, 'current_page': 'flightlogs'}  
    html_string = render_to_string('drones/flightlog_detail_pdf.html', context)
    with tempfile.NamedTemporaryFile(delete=True, suffix=".pdf") as tmp_file:
        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(tmp_file.name)
        tmp_file.seek(0)
        response = HttpResponse(tmp_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="FlightLog_{log.pk}.pdf"'
        return response

def safe_float(value):
    try:
        return float(re.sub(r'[^0-9.-]', '', value)) if value else None
    except:
        return None

def safe_int(value):
    try:
        return int(float(re.sub(r'[^0-9.-]', '', value))) if value else None
    except:
        return None


@login_required
def upload_flightlog_csv(request):
    if request.method == 'POST':
        form = FlightLogCSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['csv_file']
            decoded = file.read().decode('utf-8-sig').splitlines()
            reader = csv.DictReader(decoded)
            reader.fieldnames = [field.replace('\ufeff', '').strip() for field in reader.fieldnames]
            for row in reader:
                row = {k.strip(): (v.strip() if v else "") for k, v in row.items()}
                if not row.get("Flight/Service Date"):
                    print("Skipping row: missing Flight/Service Date")
                    continue

                # Parse date/time
                try:
                    clean_dt = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', row["Flight/Service Date"])
                    dt = datetime.strptime(clean_dt, "%b %d, %Y %I:%M%p")
                    flight_date = dt.date()
                    landing_time = dt.time()
                except Exception as e:
                    print("Skipping row: invalid date format", e)
                    continue

                try:
                    air_seconds = safe_int(row.get("Air Seconds")) or 0
                    air_time = timedelta(seconds=air_seconds)

                    FlightLog.objects.create(
                        flight_date=flight_date,
                        flight_title=row.get("Flight Title", ""),
                        flight_description=row.get("Flight Description", ""),
                        pilot_in_command=row.get("Pilot-in-Command", ""),
                        license_number=row.get("License Number", ""),
                        takeoff_latlong=row.get("Takeoff Lat/Long", ""),
                        takeoff_address=row.get("Takeoff Address", ""),
                        landing_time=landing_time,
                        air_time=air_time,
                        above_sea_level_ft=safe_float(row.get("Above Sea Level (Feet)")),
                        drone_name=row.get("Drone Name", ""),
                        drone_type=row.get("Drone Type", ""),
                        drone_serial=row.get("Drone Serial Number", ""),
                        battery_name=row.get("Battery Name", ""),
                        battery_serial_printed=row.get("Bat Printed Serial", ""),
                        battery_serial_internal=row.get("Bat Internal Serial", ""),
                        landing_battery_pct=safe_int(row.get("Landing Bat %").replace("%", "")),
                        landing_mah=safe_int(row.get("Landing mAh")),
                        landing_volts=safe_float(row.get("Landing Volts")),
                        max_altitude_ft=safe_float(row.get("Max Altitude (Feet)")),
                        max_distance_ft=safe_float(row.get("Max Distance (Feet)")),
                        max_speed_mph=safe_float(row.get("Max Speed (mph)")),
                        total_mileage_ft=safe_float(row.get("Total Mileage (Feet)")),
                        avg_wind=safe_float(row.get("Avg Wind")),
                        max_gust=safe_float(row.get("Max Gust")),
                        ground_weather_summary=row.get("Ground Weather Summary", ""),
                        ground_temp_f=safe_float(row.get("Ground Temperature (f)")),
                        visibility_miles=safe_float(row.get("Ground Visibility (Miles)")),
                        wind_speed=safe_float(row.get("Ground Wind Speed")),
                        wind_direction=row.get("Ground Wind Direction", ""),
                        cloud_cover=row.get("Cloud Cover", "").replace("%", ""),
                        signal_losses=safe_int(row.get("Signal Losses (>1 sec)")),
                        photos=safe_int(row.get("Photos")),
                        videos=safe_int(row.get("Videos")),
                        notes=row.get("Add Additional Notes", ""),
                        tags=row.get("Tags", ""),
                    )
                except Exception as e:
                    print("Row error:", e, row)
                    continue
            return redirect('flightlog_list')
    else:
        form = FlightLogCSVUploadForm()

    context = {'form': form, 'current_page': 'flightlogs'}  
    return render(request, 'drones/upload_log.html', context)
