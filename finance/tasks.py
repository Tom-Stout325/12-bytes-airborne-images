from celery import shared_task
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from weasyprint import HTML
from django.conf import settings
from .models import Invoice

@shared_task(bind=True, max_retries=3)
def send_invoice_email_task(self, invoice_id, base_url):
    try:
        invoice = Invoice.objects.get(pk=invoice_id)
        html_string = render_to_string('finance/invoice_detail.html', {'invoice': invoice, 'current_page': 'invoices'})
        html = HTML(string=html_string, base_url=base_url)
        pdf_file = html.write_pdf()
        subject = f"Invoice #{invoice.invoice_numb} from Airborne Images"
        body = f"""
        Hi {invoice.client.first},<br><br>
        Attached is your invoice for the event: <strong>{invoice.event}</strong>.<br><br>
        Let me know if you have any questions!<br><br>
        Thank you!,<br>
        <strong>Tom Stout</strong><br>
        Airborne Images<br>
        <a href="http://www.airborneimages.com" target="_blank">www.AirborneImages.com</a><br>
        "Views From Above!"<br>
        """
        email = EmailMessage(
            subject,
            body,
            'tom@tom-stout.com',
            [invoice.client.email or getattr(settings, 'DEFAULT_EMAIL', 'fallback@example.com')],
        )
        email.content_subtype = 'html'
        email.attach(f"Invoice_{invoice.invoice_numb}.pdf", pdf_file, "application/pdf")
        email.send()
    except Exception as e:
        self.retry(countdown=60, exc=e)