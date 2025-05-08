from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.core.mail import EmailMessage
from django.utils.timezone import now
from django.contrib import messages
from django.db.models import Sum, Q
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from datetime import datetime
from weasyprint import HTML
from pathlib import Path
import tempfile
import logging
import base64
import csv
import os

from .models import *
from .forms import *

logger = logging.getLogger(__name__)

class Dashboard(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/dashboard.html"
    context_object_name = "transactions"
    paginate_by = 20

    def get_queryset(self):
        return Transaction.objects.select_related('trans_type', 'sub_cat').order_by('-date')[:50]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        current_year = now.year
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_of_month = now.replace(day=28).replace(day=1).replace(month=now.month + 1) - timezone.timedelta(days=1)
        end_of_month = end_of_month.replace(hour=23, minute=59, second=59, microsecond=999999)

        # Recent and unpaid invoices
        context['recent_invoices'] = Invoice.objects.order_by('-date')[:20]
        context['unpaid_invoices'] = Invoice.objects.filter(status='Unpaid')

        # Categories
        context['categories'] = Category.objects.all()

        # Current month totals
        transactions_this_month = Transaction.objects.filter(date__gte=start_of_month, date__lte=end_of_month)
        context['income_total'] = transactions_this_month.filter(trans_type__trans_type="Income").aggregate(Sum('amount'))['amount__sum'] or 0
        context['expense_total'] = transactions_this_month.filter(trans_type__trans_type="Expense").aggregate(Sum('amount'))['amount__sum'] or 0

        # YTD summary
        try:
            start_of_year = timezone.datetime(current_year, 1, 1, tzinfo=timezone.utc)
            ytd_subcategory_totals = (
                Transaction.objects
                .filter(date__gte=start_of_year, sub_cat__isnull=False, trans_type__isnull=False)
                .values('sub_cat__sub_cat', 'trans_type__trans_type')
                .annotate(total=Sum('amount'))
                .order_by('sub_cat__sub_cat', 'trans_type__trans_type')
            )
            ytd_income_total = sum(item['total'] for item in ytd_subcategory_totals if item['trans_type__trans_type'] == 'Income')
            ytd_expense_total = sum(item['total'] for item in ytd_subcategory_totals if item['trans_type__trans_type'] == 'Expense')
            ytd_net_profit = ytd_income_total - ytd_expense_total
        except Exception as e:
            logger.error(f"Error calculating YTD data: {e}")
            ytd_subcategory_totals = []
            ytd_income_total = ytd_expense_total = ytd_net_profit = 0

        context.update({
            'ytd_subcategory_totals': ytd_subcategory_totals,
            'current_year': current_year,
            'ytd_income_total': ytd_income_total,
            'ytd_expense_total': ytd_expense_total,
            'ytd_net_profit': ytd_net_profit,
        })

        # Mileage
        try:
            mileage_rate = MileageRate.objects.get(id=1).rate
        except MileageRate.DoesNotExist:
            mileage_rate = 0.70

        taxable_miles = Miles.objects.filter(mileage_type='Taxable', date__year=current_year)
        total_miles = taxable_miles.aggregate(Sum('total'))['total__sum'] or 0
        taxable_dollars = total_miles * mileage_rate

        context.update({
            'mileage_list': Miles.objects.filter(date__year=current_year).order_by('-date'),
            'mileage_rate': mileage_rate,
            'total_miles': total_miles,
            'taxable_dollars': taxable_dollars,
        })

        return context


# Transactions   =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


class Transactions(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/transactions.html"
    paginate_by = 50
    context_object_name = "transactions"

    def get_queryset(self):
        queryset = Transaction.objects.select_related('trans_type', 'category', 'sub_cat', 'team').order_by('-date')

        year = self.request.GET.get('year')
        trans_type = self.request.GET.get('type')
        sub_cat_id = self.request.GET.get('sub_cat')

        if year:
            try:
                queryset = queryset.filter(date__year=int(year))
            except ValueError:
                logger.warning(f"Invalid year value: {year}")

        if trans_type in ['Income', 'Expense']:
            queryset = queryset.filter(trans_type__trans_type=trans_type)

        if sub_cat_id:
            queryset = queryset.filter(sub_cat__id=sub_cat_id)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'page_title': 'Transactions',
            'years': Transaction.objects.dates('date', 'year', order='DESC').distinct(),
            'sub_categories': SubCategory.objects.order_by('sub_cat'),
            'selected_year': self.request.GET.get('year', ''),
            'selected_type': self.request.GET.get('type', ''),
            'selected_sub_cat': self.request.GET.get('sub_cat', '')
        })
        return context



@login_required
def download_transactions(request):
    year = request.GET.get('year')
    trans_type = request.GET.get('type')
    queryset = Transaction.objects.select_related('trans_type', 'category', 'sub_cat', 'team').order_by('-date')
    if year:
        queryset = queryset.filter(date__year=year)
    if trans_type:
        queryset = queryset.filter(trans_type__trans_type__iexact=trans_type)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'
    writer = csv.DictWriter(response, fieldnames=['Date', 'Type', 'Transaction', 'Location', 'Amount', 'Invoice #'])
    writer.writeheader()
    try:
        for transaction in queryset:
            writer.writerow({
                'Date': transaction.date,
                'Type': transaction.trans_type,
                'Transaction': transaction.transaction,
                'Location': transaction.keyword,
                'Amount': transaction.amount,
                'Invoice #': transaction.invoice_numb,
            })
    except Exception as e:
        logger.error(f"Error writing CSV: {e}")
        return HttpResponse("Error generating CSV", status=500)
    return response


@login_required
def add_transaction(request):
    if request.method == "POST":
        form = TransForm(request.POST, request.FILES)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.user = request.user
            transaction.save()
            messages.success(request, 'Transaction added successfully!')
            return redirect('add_transaction_success')
        else:
            messages.error(request, 'Error adding transaction. Please check the form.')
    else:
        form = TransForm()
    return render(request, 'finance/transaction_add.html', {'form': form})


@login_required
def add_transaction_success(request):
    return render(request, 'finance/transaction_add_success.html')


@login_required
def transaction_detail_page(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    return render(request, 'finance/transactions_detail_view.html', {'transaction': transaction})


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"

    def get_success_url(self):
        return self.request.GET.get('next', reverse('transactions'))

    def get_object(self, queryset=None):
        return get_object_or_404(Transaction, pk=self.kwargs['pk'])

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Transaction deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def edit_transaction(request, transaction_id):
    transaction = get_object_or_404(Transaction, id=transaction_id)
    if request.method == 'POST':
        form = TransForm(request.POST, request.FILES, instance=transaction)
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated successfully!')
            return redirect('transactions')
        else:
            messages.error(request, 'Error updating transaction. Please check the form.')
            logger.error(f"Form errors: {form.errors}")
    else:
        form = TransForm(instance=transaction)
    return render(request, 'finance/transaction_edit.html', {'transaction': transaction, 'form': form})



@login_required
def transaction_delete(request, pk):
    transaction = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        transaction.delete()
        messages.success(request, "Transaction was deleted.")
        return redirect('transactions')
    return render(request, 'finance/transaction_confirm_delete.html', {'item': transaction})





# Invoices   =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


@login_required
def create_invoice(request):
    if request.method == 'POST':
        form = InvoiceForm(request.POST)
        formset = InvoiceItemFormSet(request.POST)

        if form.is_valid() and formset.is_valid():
            invoice = form.save(commit=False)
            invoice.amount = 0  # placeholder
            invoice.save()

            items = formset.save(commit=False)
            for item in items:
                item.invoice = invoice
                item.save()

            invoice.amount = invoice.calculate_total()
            invoice.save()

            messages.success(request, f"Invoice #{invoice.invoice_numb} created successfully.")
            return redirect('invoice_list')
    else:
        form = InvoiceForm()
        formset = InvoiceItemFormSet()

    return render(request, 'finance/invoice_add.html', {
        'form': form,
        'formset': formset
    })


@login_required
def update_invoice(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        form = InvoiceForm(request.POST, instance=invoice)
        formset = InvoiceItemFormSet(request.POST, instance=invoice)

        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()

            invoice.amount = invoice.calculate_total()
            invoice.save()
            messages.success(request, f"Invoice # {invoice.invoice_numb} Updated successfully.")
            return redirect('invoice_list')
        else:
            print("FORM ERRORS:", form.errors)
            print("FORMSET ERRORS:", formset.errors)
    else:
        form = InvoiceForm(instance=invoice)
        formset = InvoiceItemFormSet(instance=invoice)

    return render(request, 'finance/invoice_update.html', {
        'form': form,
        'formset': formset,
        'invoice': invoice
    })


def create_invoice_success(request):
    return render(request, 'finance/invoice_add_success.html')



class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "finance/invoices.html"
    context_object_name = "invoices"
    paginate_by = 10

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'invoice_numb')
        direction = self.request.GET.get('direction', 'desc')
        ordering = f"-{sort}" if direction == "desc" else sort

        queryset = Invoice.objects.order_by(ordering)

        search_query = self.request.GET.get('search', '')
        if search_query:
            queryset = queryset.filter(
                Q(invoice_numb__icontains=search_query) |
                Q(client__business__icontains=search_query) |
                Q(service__service__icontains=search_query)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get('search', '')
        context["current_sort"] = self.request.GET.get('sort', 'invoice_numb')
        context["current_direction"] = self.request.GET.get('direction', 'desc')
        context["new_direction"] = "asc" if context["current_direction"] == "desc" else "desc"
        context["invoice_headers"] = [
            ("invoice_numb", "Invoice #"),
            ("client__business", "Client"),
            ("keyword", "Location"),
            ("service__service", "Service"),
            ("amount", "Amount"),
            ("date", "Date"),
            ("due", "Due"),
            ("paid_date", "Paid"),
            ("days_to_pay", "Days to Pay"),
        ]
        return context




class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'finance/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logo_path = os.path.join(settings.STATIC_ROOT or settings.STATICFILES_DIRS[0], 'images', 'logo2.png')
        if not os.path.exists(logo_path):
            context['logo_path'] = None
        else:
            context['logo_path'] = f'file://{logo_path}'
        context['rendering_for_pdf'] = self.request.GET.get('pdf', False)
        return context


@login_required
def invoice_review(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    transactions = Transaction.objects.filter(invoice_numb=invoice.invoice_numb)
    total_expenses = transactions.filter(trans_type__trans_type='Expense').aggregate(total=Sum('amount'))['total'] or 0
    total_income = transactions.filter(trans_type__trans_type='Income').aggregate(total=Sum('amount'))['total'] or 0
    net_amount = total_income - total_expenses
    return render(request, 'finance/invoice_review.html', {
        'invoice': invoice,
        'transactions': transactions,
        'total_expenses': total_expenses,
        'total_income': total_income,
        'net_amount': net_amount,
        'invoice_amount': invoice.amount,
    })


@login_required
def unpaid_invoices(request):
    invoices = Invoice.objects.filter(paid__iexact="No").order_by('due_date')
    return render(request, 'components/unpaid_invoices.html', {'invoices': invoices})


@login_required
def invoice_delete(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    if request.method == 'POST':
        invoice.delete()
        messages.success(request, "Invoice was deleted.")
        return redirect('invoice_list')
    return render(request, 'finance/invoice_confirm_delete.html', {'item': invoice})


def export_invoices_pdf(request):
    sort = request.GET.get('sort', 'invoice_numb')
    direction = request.GET.get('direction', 'desc')
    ordering = f"-{sort}" if direction == "desc" else sort
    search = request.GET.get('search', '')

    invoices = Invoice.objects.order_by(ordering)
    if search:
        invoices = invoices.filter(
            Q(invoice_numb__icontains=search) |
            Q(client__business__icontains=search) |
            Q(service__service__icontains=search)
        )

    template = get_template('finance/invoice_pdf_export.html')
    html_string = template.render({'invoices': invoices})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoices.pdf"'

    with tempfile.NamedTemporaryFile(delete=True) as output:
        HTML(string=html_string).write_pdf(output.name)
        output.seek(0)
        response.write(output.read())

    return response


def export_invoices_csv(request):
    sort = request.GET.get('sort', 'invoice_numb')
    direction = request.GET.get('direction', 'desc')
    ordering = f"-{sort}" if direction == "desc" else sort
    search = request.GET.get('search', '')

    invoices = Invoice.objects.order_by(ordering)
    if search:
        invoices = invoices.filter(
            Q(invoice_numb__icontains=search) |
            Q(client__business__icontains=search) |
            Q(service__service__icontains=search)
        )

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="invoices.csv"'

    writer = csv.writer(response)
    writer.writerow(['Invoice #', 'Client', 'Location', 'Service', 'Amount', 'Date', 'Due', 'Paid', 'Days to Pay'])

    for invoice in invoices:
        writer.writerow([
            invoice.invoice_numb,
            str(invoice.client),
            invoice.keyword,
            str(invoice.service),
            invoice.amount,
            invoice.date,
            invoice.due,
            invoice.paid_date or "No",
            invoice.days_to_pay if invoice.paid_date else "—"
        ])
    return response

def export_invoices_pdf(request):
    sort = request.GET.get('sort', 'invoice_numb')
    direction = request.GET.get('direction', 'desc')
    ordering = f"-{sort}" if direction == "desc" else sort
    search = request.GET.get('search', '')

    invoices = Invoice.objects.order_by(ordering)
    if search:
        invoices = invoices.filter(
            Q(invoice_numb__icontains=search) |
            Q(client__business__icontains=search) |
            Q(service__service__icontains=search)
        )

    template = get_template('finance/invoice_pdf_export.html')
    html_string = template.render({'invoices': invoices})

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="invoices.pdf"'

    with tempfile.NamedTemporaryFile(delete=True) as output:
        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(output.name)
        output.seek(0)
        response.write(output.read())

    return response



def invoice_review_pdf(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    transactions = Transaction.objects.filter(invoice_numb=invoice.invoice_numb)
    
    context = {
        'invoice': invoice,
        'transactions': transactions,
        'invoice_amount': invoice.amount,
        'total_expenses': sum(t.amount for t in transactions),
        'net_amount': invoice.amount - sum(t.amount for t in transactions),
    }

    template = get_template('finance/invoice_review_pdf.html')
    html_string = template.render(context)

    if request.GET.get("preview") == "1":
        return HttpResponse(html_string)

    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(tmp.name)
        tmp.seek(0)
        return HttpResponse(tmp.read(), content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="invoice_{invoice.invoice_numb}.pdf"'
        })


# Categories    =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def category_page(request):
    category = Category.objects.order_by('category')        
    sub_cat = SubCategory.objects.order_by('sub_cat')   

    context = {
        'category': category,
        'sub_cat': sub_cat,
    }
    return render(request, 'finance/category_page.html', context)



# class CategoryListView(LoginRequiredMixin, ListView):
#     model = Category
#     template_name = "components/category_page.html"
#     context_object_name = "categories"
#     ordering = ['category']


class CategoryCreateView(LoginRequiredMixin, CreateView):
    model = Category 
    form_class = CategoryForm
    template_name = "components/category_form.html"
    success_url = reverse_lazy('category_page')

    def form_valid(self, form):
        messages.success(self.request, "Category added successfully!")
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "components/category_form.html"
    success_url = reverse_lazy('category_page')

    def form_valid(self, form):
        messages.success(self.request, "Category updated successfully!")
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Category
    template_name = "components/category_confirm_delete.html"
    success_url = reverse_lazy('category_page')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Category deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Sub-Categories  =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-



class SubCategoryCreateView(LoginRequiredMixin, CreateView):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = "components/sub_category_form.html"
    success_url = reverse_lazy('category_page')

    def form_valid(self, form):
        messages.success(self.request, "Sub-Category added successfully!")
        return super().form_valid(form)


class SubCategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = SubCategory
    form_class = SubCategoryForm
    template_name = "components/sub_category_form.html"
    success_url = reverse_lazy('category_page')
    context_object_name = "sub_cat"

    def form_valid(self, form):
        messages.success(self.request, "Sub-Category updated successfully!")
        return super().form_valid(form)


class SubCategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = SubCategory
    template_name = "components/sub_category_confirm_delete.html"
    success_url = reverse_lazy('category_page')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Sub-Category deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Clients   =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

class ClientListView(LoginRequiredMixin, ListView):
    model = Client
    template_name = "components/client_list.html"
    context_object_name = "clients"
    ordering = ['business']


class ClientCreateView(LoginRequiredMixin, CreateView):
    model = Client
    form_class = ClientForm
    template_name = "components/client_form.html"
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, "Client added successfully!")
        return super().form_valid(form)


class ClientUpdateView(LoginRequiredMixin, UpdateView):
    model = Client
    form_class = ClientForm
    template_name = "components/client_form.html"
    success_url = reverse_lazy('client_list')

    def form_valid(self, form):
        messages.success(self.request, "Client updated successfully!")
        return super().form_valid(form)


class ClientDeleteView(LoginRequiredMixin, DeleteView):
    model = Client
    template_name = "components/client_confirm_delete.html"
    success_url = reverse_lazy('client_list')

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Client deleted successfully!")
        return super().delete(request, *args, **kwargs)


# Financial Reports  =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def get_summary_data(transactions, year):
    if year:
        transactions = transactions.filter(date__year=year)
    income_transactions = transactions.filter(trans_type__trans_type="Income")
    expense_transactions = transactions.filter(trans_type__trans_type="Expense")

    income_category_totals = income_transactions.values('category__category').annotate(total=Sum('amount')).order_by('-total')
    expense_category_totals = expense_transactions.values('category__category').annotate(total=Sum('amount')).order_by('-total')
    income_subcategory_totals = income_transactions.values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('-total')
    expense_subcategory_totals = expense_transactions.values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('-total')

    income_category_total = sum(x['total'] or 0 for x in income_category_totals)
    expense_category_total = sum(x['total'] or 0 for x in expense_category_totals)
    income_subcategory_total = sum(x['total'] or 0 for x in income_subcategory_totals)
    expense_subcategory_total = sum(x['total'] or 0 for x in expense_subcategory_totals)
    net_profit = income_category_total - expense_category_total

    return {
        'income_category_totals': income_category_totals,
        'expense_category_totals': expense_category_totals,
        'income_subcategory_totals': income_subcategory_totals,
        'expense_subcategory_totals': expense_subcategory_totals,
        'income_category_total': income_category_total,
        'expense_category_total': expense_category_total,
        'income_subcategory_total': income_subcategory_total,
        'expense_subcategory_total': expense_subcategory_total,
        'selected_year': year,
        'net_profit': net_profit
    }

@login_required
def financial_statement(request):
    current_year = timezone.now().year
    year = request.GET.get('year', str(current_year))
    transactions = Transaction.objects.select_related('trans_type', 'sub_cat')
    if year:
        transactions = transactions.filter(date__year=year)
    income_transactions = transactions.filter(trans_type__trans_type="Income").values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('-total')
    expense_transactions = transactions.filter(trans_type__trans_type="Expense").values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('-total')
    total_income = sum(item['total'] for item in income_transactions)
    total_expenses = sum(item['total'] for item in expense_transactions)
    net_profit = total_income - total_expenses
    available_years = Transaction.objects.dates('date', 'year').distinct()
    return render(request, 'finance/financial_statement.html', {
        'income_transactions': income_transactions,
        'expense_transactions': expense_transactions,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'net_profit': net_profit,
        'selected_year': year,
        'available_years': available_years,
    })



@login_required
def print_category_summary(request):
    year = request.GET.get('year')
    transactions = (
        Transaction.objects
        .filter(user=request.user)
        .select_related('trans_type', 'category', 'sub_cat')
    )
    context = get_summary_data(transactions, year)
    return render(request, 'finance/category_summary_print.html', context)



@login_required
def category_summary(request):
    year = request.GET.get('year', str(timezone.now().year))
    transactions = (
        Transaction.objects
        .filter(user=request.user)
        .select_related('trans_type', 'category', 'sub_cat')
    )
    context = get_summary_data(transactions, year)
    context['available_years'] = (
        Transaction.objects.filter(user=request.user)
        .dates('date', 'year')
        .distinct()
    )
    return render(request, 'finance/category_summary.html', context)



@login_required
def keyword_financial_summary(request):
    current_year = timezone.now().year
    years = [current_year, current_year - 1, current_year - 2]
    excluded_keywords = {"na", "monthly", "nhra", "none", "Denver", "None", "Monthly", "NHRA"}
    summary_data = (
        Transaction.objects
        .exclude(keyword__name__in=excluded_keywords)
        .filter(date__year__in=years)
        .values('keyword__name', 'date__year', 'trans_type__trans_type')
        .annotate(total=Sum('amount'))
        .order_by('keyword__name', 'date__year')
    )

    result = {}
    for item in summary_data:
        keyword = item['keyword__name']
        year = item['date__year']
        trans_type = item['trans_type__trans_type'].lower()
        if keyword not in result:
            result[keyword] = {y: {"income": 0, "expense": 0, "net": 0} for y in years}
        if trans_type == "income":
            result[keyword][year]["income"] = item['total']
        elif trans_type == "expense":
            result[keyword][year]["expense"] = item['total']
        result[keyword][year]["net"] = result[keyword][year]["income"] - result[keyword][year]["expense"]

    return render(request, "finance/keyword_financial_summary.html", {
        "years": years,
        "summary_data": result,
    })


@login_required
def reports_page(request):
    return render(request, 'finance/reports.html')



# Emails =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


@require_POST
def send_invoice_email(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    html_string = render_to_string('finance/invoice_detail.html', {'invoice': invoice})
    html = HTML(string=html_string, base_url=request.build_absolute_uri())

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

    from_email = "tom@tom-stout.com"
    recipient = ["tom.stout97@gmail.com"]

    email = EmailMessage(subject, body, from_email, recipient)
    email.content_subtype = 'html'
    email.attach(f"Invoice_{invoice.invoice_numb}.pdf", pdf_file, "application/pdf")
    email.send()

    return render(request, 'finance/email_sent.html')



# Mileage =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

@login_required
def mileage_list(request):
    try:
        mileage_rate = MileageRate.objects.get(id=1).rate
    except MileageRate.DoesNotExist:
        mileage_rate = 0.70

    current_year = datetime.now().year
    mileage_entries = Miles.objects.filter(date__year=current_year)

    taxable_miles = mileage_entries.filter(mileage_type='Taxable')
    total_miles = taxable_miles.aggregate(Sum('total'))['total__sum'] or 0

    taxable_miles_total = taxable_miles.aggregate(Sum('total'))['total__sum'] or 0
    taxable_dollars = taxable_miles_total * mileage_rate

    return render(request, 'finance/dashboard.html', {
        'mileage_list': mileage_entries,
        'total_miles': total_miles,
        'taxable_dollars': taxable_dollars,
        'current_year': current_year,
        'mileage_rate': mileage_rate,
    })


@login_required
def mileage_log(request):
    try:
        mileage_rate = MileageRate.objects.get(id=1).rate
    except MileageRate.DoesNotExist:
        mileage_rate = 0.70

    current_year = datetime.now().year
    mileage_entries = Miles.objects.filter(date__year=current_year)

    taxable_miles = mileage_entries.filter(mileage_type='Taxable')
    total_miles = taxable_miles.aggregate(Sum('total'))['total__sum'] or 0

    taxable_miles_total = taxable_miles.aggregate(Sum('total'))['total__sum'] or 0
    taxable_dollars = taxable_miles_total * mileage_rate

    return render(request, 'finance/mileage_log.html', {
        'mileage_list': mileage_entries,
        'total_miles': total_miles,
        'taxable_dollars': taxable_dollars,
        'current_year': current_year,
        'mileage_rate': mileage_rate,
    })


class MileageCreateView(LoginRequiredMixin, CreateView):
    model = Miles
    form_class = MileageForm
    template_name = 'finance/mileage_form.html'
    success_url = reverse_lazy('dashboard')


class MileageUpdateView(LoginRequiredMixin, UpdateView):
    model = Miles
    form_class = MileageForm
    template_name = 'finance/mileage_form.html'
    success_url = reverse_lazy('dashboard')


class MileageDeleteView(LoginRequiredMixin, DeleteView):
    model = Miles
    template_name = 'finance/mileage_confirm_delete.html'
    success_url = reverse_lazy('dashboard')
    

@login_required
def add_mileage(request):
    if request.method == "POST":
        form = MileageForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('mileage_list')
    else:
        form = MileageForm()
        
    context = {
        'form': form,
    }
    return render(request, 'finance/mileage_form.html', context)


@login_required
def update_mileage_rate(request):
    mileage_rate, created = MileageRate.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = MileageRateForm(request.POST, instance=mileage_rate)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = MileageRateForm(instance=mileage_rate)

    return render(request, 'components/update_mileage_rate.html', {'form': form})



