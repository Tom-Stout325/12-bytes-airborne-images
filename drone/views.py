from django.shortcuts import render, redirect, get_object_or_404
from formtools.wizard.views import SessionWizardView
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.core.paginator import Paginator
from django.template import RequestContext
from django.http import HttpResponse
from django.utils import timezone
from django.conf import settings
from operator import attrgetter
from django.db.models import Q
from itertools import groupby
from weasyprint import HTML 
import uuid
import os
from weasyprint import HTML
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import *
from .models import *



@login_required
def documents(request):
    return render(request, 'drones/documents.html')


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
    }
    return render(request, 'drones/incident_reporting_system.html', context)


@login_required
def incident_report_pdf(request, pk):
    report = get_object_or_404(DroneIncidentReport, pk=pk)

    # Full path to static logo for PDF rendering
    logo_path = request.build_absolute_uri(static("images/logo2.png"))

    # Render the HTML template to a string
    html_string = render_to_string(
        'drones/incident_report_pdf.html',
        {
            'report': report,
            'logo_path': logo_path,
            'now': timezone.now()
        },
        request=request
    )
    print("USING HTML CONSTRUCTOR:", HTML.__init__)
    print("USING MODULE:", HTML.__module__)

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

class IncidentReportWizard(LoginRequiredMixin, SessionWizardView):
    template_name = 'drones/incident_report_form.html'

    def get(self, request, *args, **kwargs):
        self._storage = self.get_wizard_storage()
        self._storage.reset()
        return super().get(request, *args, **kwargs)

    def get_wizard_storage(self):
        self.storage 
        return self.storage

    def get_context_data(self, form, **kwargs):
        context = super().get_context_data(form=form, **kwargs)
        current_step = self.steps.step1 + 1
        total_steps = self.steps.count
        progress_percent = int((current_step / total_steps) * 100)
        context.update({
            'current_step': current_step,
            'total_steps': total_steps,
            'progress_percent': progress_percent,
        })
        return context


    def done(self, form_list, **kwargs):
        data = {}
        for form in form_list:
            data.update(form.cleaned_data)

        report = DroneIncidentReport.objects.create(**data)
        html_string = render_to_string('drones/incident_report_pdf.html', {'report': report}, request=self.request)
        html = HTML(string=html_string, base_url=self.request.build_absolute_uri())
        pdf_content = html.write_pdf()
        unique_id = uuid.uuid4()
        filename = f'reports/incident_report_{report.pk}_{unique_id}.pdf'
        filepath = os.path.join(settings.MEDIA_ROOT, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, 'wb') as f:
            f.write(pdf_content)

        pdf_url = os.path.join(settings.MEDIA_URL, filename)

        return render(self.request, 'drones/incident_report_success.html', {
            'form_data': data,
            'pdf_url': pdf_url,
        })

@login_required
def incident_report_success(request):
    pdf_url = request.GET.get('pdf_url', None) 
    return render(request, 'drones/report_success.html', {'pdf_url': pdf_url})

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
    print("Incident report count:", reports.count())
    context = {
        'incident_reports': reports.order_by('-report_date'),
        'search_query': query
    }
    def incident_report_list(request):
        print("DB path (view):", settings.DATABASES['default']['NAME'])
        reports = DroneIncidentReport.objects.all()
        print("From view:", reports.count())

    return render(request, 'drones/incident_list.html', context)


@login_required
def incident_report_detail(request, pk):
    report = get_object_or_404(DroneIncidentReport, pk=pk)
    return render(request, 'drones/incident_report_detail.html', {'report': report})


@login_required
def sop_upload(request):
    if request.method == 'POST':
        form = SOPDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('sop_list')
    else:
        form = SOPDocumentForm()
    return render(request, 'sop_manager/sop_upload.html', {'form': form})


@login_required
def sop_list(request):
    sops = SOPDocument.objects.order_by('-created_at')
    paginator = Paginator(sops, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'sop_manager/sop_list.html', {
        'sops': page_obj,
        'page_obj': page_obj,
    })


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
    }
    return render(request, 'drones/general_list.html', context)

@login_required
def upload_general_document(request):
    if request.method == 'POST':
        form = GeneralDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('general_document_list')
    else:
        form = GeneralDocumentForm()
    return render(request, 'drones/upload_general.html', {'form': form})


@login_required
def equipment_list(request):
    equipment = Equipment.objects.all().order_by('-purchase_date')
    return render(request, 'drones/equipment_list.html', {'equipment': equipment})

@login_required
def equipment_create(request):
    if request.method == 'POST':
        form = EquipmentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm()
    return render(request, 'drones/equipment_form.html', {'form': form, 'title': 'Add Equipment'})

@login_required
def equipment_edit(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        form = EquipmentForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('equipment_list')
    else:
        form = EquipmentForm(instance=item)
    return render(request, 'drones/equipment_form.html', {'form': form, 'title': 'Edit Equipment'})

@login_required
def equipment_delete(request, pk):
    item = get_object_or_404(Equipment, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('equipment_list')
    return render(request, 'drones/equipment_confirm_delete.html', {'item': item})

