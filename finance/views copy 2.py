from django.views.generic import ListView, DetailView, UpdateView, DeleteView, CreateView, TemplateView
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.http import JsonResponse, HttpResponse
from django.db.models.functions import ExtractYear
from django.db.models.functions import TruncMonth
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.core.mail import EmailMessage
from django.utils.timezone import now
from django.contrib import messages
from collections import defaultdict
from django.db.models import Sum, Q
from django.utils import timezone
from django.conf import settings
from calendar import monthrange
from calendar import month_name
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
from django.views import View  


class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "finance/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add URLs for navigation cards
        context['navigation'] = {
            'transactions': reverse_lazy('transactions'),
            'invoices': reverse_lazy('invoice_list'),
            'reports': reverse_lazy('reports_page'),
            'mileage': reverse_lazy('mileage_log'),
            'categories': reverse_lazy('category_page'),
            'clients': reverse_lazy('client_list'),
            'keywords': reverse_lazy('keyword_list'),
            'recurring_transactions': reverse_lazy('recurring_list'),
        }
        return context


@login_required
def transaction_search(request):
    current_year = now().year
    selected_keyword = request.GET.get('keyword', '')
    selected_category = request.GET.get('category', '')
    selected_sub_cat = request.GET.get('sub_cat', '')
    selected_year = request.GET.get('year', '')
    queryset = Transaction.objects.select_related('trans_type', 'category', 'sub_cat', 'keyword')

    if selected_keyword:
        queryset = queryset.filter(keyword__id=selected_keyword)
    if selected_category:
        queryset = queryset.filter(category__id=selected_category)
    if selected_sub_cat:
        queryset = queryset.filter(sub_cat__id=selected_sub_cat)
    if selected_year:
        queryset = queryset.filter(date__year=selected_year)

    years_qs = Transaction.objects.annotate(extracted_year=ExtractYear('date')) \
                                  .values_list('extracted_year', flat=True) \
                                  .distinct() \
                                  .order_by('-extracted_year')

    years = [str(y) for y in years_qs if y is not None]

    context = {
        'transactions': queryset,
        'categories': Category.objects.order_by('category'),
        'sub_categories': SubCategory.objects.order_by('sub_cat'),
        'keyword_options': Keyword.objects.all(),
        'years': years,
        'selected_keyword': selected_keyword,
        'selected_category': selected_category,
        'selected_sub_cat': selected_sub_cat,
        'selected_year': selected_year,
    }

    return render(request, 'finance/transaction_search.html', context)


# Transactions   =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


class Transactions(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/transactions.html"
    context_object_name = "transactions"
    paginate_by = 50

    def get_queryset(self):
        queryset = Transaction.objects.select_related(
            'trans_type', 'category', 'sub_cat', 'team', 'keyword'
        )

        # Apply filters
        keyword_id = self.request.GET.get('keyword')
        if keyword_id:
            queryset = queryset.filter(keyword__id=keyword_id)

        category_id = self.request.GET.get('category')
        if category_id:
            queryset = queryset.filter(category__id=category_id)

        sub_cat_id = self.request.GET.get('sub_cat')
        if sub_cat_id:
            queryset = queryset.filter(sub_cat__id=sub_cat_id)

        # Apply sorting
        sort = self.request.GET.get('sort', '-date')  # Default to descending date
        valid_sort_fields = [
            'date', '-date',
            'trans_type', '-trans_type',
            'transaction', '-transaction',
            'keyword', '-keyword',
            'amount', '-amount',
            'invoice_numb', '-invoice_numb',
        ]
        if sort in valid_sort_fields:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by('-date')  # Fallback to default

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', '-date')
        # Add filter options
        context['keywords'] = Keyword.objects.filter(transaction__isnull=False).distinct().order_by('name')
        context['categories'] = Category.objects.filter(transaction__isnull=False).distinct().order_by('category')
        context['subcategories'] = SubCategory.objects.filter(transaction__isnull=False).distinct().order_by('sub_cat')
        return context


class DownloadTransactionsCSV(LoginRequiredMixin, View):
    def get(self, request):
        # Reuse the Transactions view's queryset logic
        transactions_view = Transactions()
        transactions_view.request = request  # Set request to access GET parameters
        queryset = transactions_view.get_queryset()

        # Filter by current year if 'year=current' is in GET parameters
        year_param = request.GET.get('year', None)
        if year_param == 'current':
            current_year = datetime.now().year
            queryset = queryset.filter(date__year=current_year)

        # Prepare CSV response
        response = HttpResponse(content_type='text/csv')
        filename = "transactions_current_year.csv" if year_param == 'current' else "transactions_all.csv"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        writer = csv.writer(response)
        writer.writerow(['Date', 'Type', 'Transaction', 'Location', 'Amount', 'Invoice #'])

        for tx in queryset:
            writer.writerow([
                tx.date,
                tx.trans_type.trans_type if tx.trans_type else '',
                tx.transaction,
                tx.keyword.name if tx.keyword else '',
                tx.amount,
                tx.invoice_numb
            ])

        return response



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


@login_required
def transaction_search(request):
    current_year = now().year

    selected_keyword = request.GET.get('keyword', '')
    selected_category = request.GET.get('category', '')
    selected_sub_cat = request.GET.get('sub_cat', '')
    selected_year = request.GET.get('year', '')

    queryset = Transaction.objects.select_related('trans_type', 'category', 'sub_cat', 'keyword')

    if selected_keyword:
        queryset = queryset.filter(keyword__id=selected_keyword)
    if selected_category:
        queryset = queryset.filter(category__id=selected_category)
    if selected_sub_cat:
        queryset = queryset.filter(sub_cat__id=selected_sub_cat)
    if selected_year:
        queryset = queryset.filter(date__year=selected_year)

    years_qs = Transaction.objects.annotate(extracted_year=ExtractYear('date')) \
                                  .values_list('extracted_year', flat=True) \
                                  .distinct() \
                                  .order_by('-extracted_year')

    years = [str(y) for y in years_qs if y is not None]

    context = {
        'transactions': queryset,
        'categories': Category.objects.order_by('category'),
        'sub_categories': SubCategory.objects.order_by('sub_cat'),
        'keyword_options': Keyword.objects.all(),
        'years': years,
        'selected_keyword': selected_keyword,
        'selected_category': selected_category,
        'selected_sub_cat': selected_sub_cat,
        'selected_year': selected_year,
    }

    return render(request, 'finance/transaction_search.html', context)


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
    paginate_by = 20

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'invoice_numb')
        direction = self.request.GET.get('direction', 'desc')
        valid_sort_fields = [
            'invoice_numb', 'client__business', 'keyword', 'service__service',
            'amount', 'date', 'due', 'paid_date', 'days_to_pay'
        ]
        if sort not in valid_sort_fields:
            sort = 'invoice_numb'
        ordering = f"-{sort}" if direction == 'desc' else sort
        queryset = Invoice.objects.select_related('client', 'keyword', 'service').order_by(ordering)
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
        context['search_query'] = self.request.GET.get('search', '')
        context['current_sort'] = self.request.GET.get('sort', 'invoice_numb')
        context['current_direction'] = self.request.GET.get('direction', 'desc')
        return context


class InvoiceDetailView(LoginRequiredMixin, DetailView):
    model = Invoice
    template_name = 'finance/invoice_detail.html'
    context_object_name = 'invoice'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        logo_path = next((os.path.join(path, 'images/logo2.png')
        for path in (settings.STATICFILES_DIRS if hasattr(settings, 'STATICFILES_DIRS') else [])
        if os.path.exists(os.path.join(path, 'images/logo2.png'))), None)

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


@login_required
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


@login_required
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


@login_required
def invoice_review_pdf(request, pk):
    invoice = Invoice.objects.get(pk=pk)
    transactions = Transaction.objects.filter(
        invoice_numb=invoice.invoice_numb,
        trans_type__trans_type__iexact="Expense"
)

    total_expenses = sum(t.amount for t in transactions)
    net_amount = invoice.amount - total_expenses

    context = {
        'invoice': invoice,
        'transactions': transactions,
        'invoice_amount': invoice.amount,
        'total_expenses': total_expenses,
        'net_amount': net_amount,
        'now': now(),
    }

    template = get_template('finance/invoice_review_pdf.html')
    html_string = template.render(context) 

    html_string = "<style>@page { size: 8.5in 11in; margin: 1in; }</style>" + html_string

    if request.GET.get("preview") == "1":
        return HttpResponse(html_string)

    with tempfile.NamedTemporaryFile(delete=True) as tmp:
        HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(tmp.name)
        tmp.seek(0)
        return HttpResponse(tmp.read(), content_type='application/pdf', headers={
            'Content-Disposition': f'attachment; filename="invoice_{invoice.invoice_numb}.pdf"'
        })


# Categories    =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


@login_required
def category_page(request):
    category = Category.objects.order_by('category')        
    sub_cat = SubCategory.objects.order_by('sub_cat')   

    context = {
        'category': category,
        'sub_cat': sub_cat,
    }
    return render(request, 'finance/category_page.html', context)


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


@login_required
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
    year = request.GET.get('year', str(timezone.now().year))
    context = get_summary_data(request, year)
    return render(request, 'finance/category_summary_print.html', context)



def get_summary_data(request, year):
    user = request.user

    # Base filter
    transactions = Transaction.objects.filter(
        user=user,
        date__year=year
    ).select_related('trans_type', 'category', 'sub_cat')

    # Income Transactions
    income = transactions.filter(trans_type__trans_type='Income')
    income_category_totals = income.values('category__category').annotate(total=Sum('amount')).order_by('category__category')
    income_subcategory_totals = income.values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('sub_cat__sub_cat')
    income_category_total = income.aggregate(total=Sum('amount'))['total'] or 0
    income_subcategory_total = income.aggregate(total=Sum('amount'))['total'] or 0

    # Expense Transactions
    expense = transactions.filter(trans_type__trans_type='Expense')
    expense_category_totals = expense.values('category__category').annotate(total=Sum('amount')).order_by('category__category')
    expense_subcategory_totals = expense.values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('sub_cat__sub_cat')
    expense_category_total = expense.aggregate(total=Sum('amount'))['total'] or 0
    expense_subcategory_total = expense.aggregate(total=Sum('amount'))['total'] or 0

    # Net Profit
    net_profit = income_category_total - expense_category_total

    return {
        'selected_year': year,
        'income_category_totals': income_category_totals,
        'income_subcategory_totals': income_subcategory_totals,
        'income_category_total': income_category_total,
        'income_subcategory_total': income_subcategory_total,
        'expense_category_totals': expense_category_totals,
        'expense_subcategory_totals': expense_subcategory_totals,
        'expense_category_total': expense_category_total,
        'expense_subcategory_total': expense_subcategory_total,
        'net_profit': net_profit,
    }



@login_required
def category_summary(request):
    year = request.GET.get('year', str(timezone.now().year))
    context = get_summary_data(request, year)
    context['available_years'] = (
        Transaction.objects.filter(user=request.user)
        .dates('date', 'year', order='DESC')
        .distinct()
    )
    return render(request, 'finance/category_summary.html', context)

    

@login_required
def nhra_summary(request):
    current_year = timezone.now().year
    years = [current_year, current_year - 1, current_year - 2]

    excluded_ids = [35, 133, 34, 67, 100]

    summary_data = (
        Transaction.objects
        .exclude(keyword__id__in=excluded_ids)
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

        result[keyword][year]["net"] = (
            result[keyword][year]["income"] - result[keyword][year]["expense"]
        )

    return render(request, "finance/nhra_summary.html", {
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
    recipient = [invoice.client.email or settings.DEFAULT_EMAIL]
    email = EmailMessage(subject, body, from_email, recipient)
    email.content_subtype = 'html'
    email.attach(f"Invoice_{invoice.invoice_numb}.pdf", pdf_file, "application/pdf")
    email.send()

    return render(request, 'finance/email_sent.html')


# Mileage =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-


def get_mileage_context(request):
    try:
        rate = MileageRate.objects.get(id=1).rate
    except MileageRate.DoesNotExist:
        rate = 0.70

    year = datetime.now().year
    entries = Miles.objects.filter(user=request.user, date__year=year)
    taxable = entries.filter(mileage_type='Taxable')
    total_miles = taxable.aggregate(Sum('total'))['total__sum'] or 0

    return {
        'mileage_list': entries,
        'total_miles': total_miles,
        'taxable_dollars': total_miles * rate,
        'current_year': year,
        'mileage_rate': rate,
    }


@login_required
def mileage_log(request):
    context = get_mileage_context(request)
    return render(request, 'finance/mileage_log.html', context)



class MileageCreateView(LoginRequiredMixin, CreateView):
    model = Miles
    form_class = MileageForm
    template_name = 'finance/mileage_form.html'
    success_url = reverse_lazy('mileage_log')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class MileageUpdateView(LoginRequiredMixin, UpdateView):
    model = Miles
    form_class = MileageForm
    template_name = 'finance/mileage_form.html'
    success_url = reverse_lazy('mileage_log')

    def get_queryset(self):
        return Miles.objects.filter(user=self.request.user)


class MileageDeleteView(LoginRequiredMixin, DeleteView):
    model = Miles
    template_name = 'finance/mileage_confirm_delete.html'
    success_url = reverse_lazy('mileage_log')

    def get_queryset(self):
        return Miles.objects.filter(user=self.request.user)


@login_required
def update_mileage_rate(request):
    mileage_rate, created = MileageRate.objects.get_or_create(id=1)

    if request.method == 'POST':
        form = MileageRateForm(request.POST, instance=mileage_rate)
        if form.is_valid():
            form.save()
            return redirect('mileage_log')
    else:
        form = MileageRateForm(instance=mileage_rate)

    return render(request, 'components/update_mileage_rate.html', {'form': form})


#-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=--=-=-=-=-=-=-=-=-=-=-=--=-= KEYWORDS


class KeywordListView(ListView):
    model = Keyword
    template_name = 'finance/keyword_list.html'
    context_object_name = 'keywords'

class KeywordCreateView(CreateView):
    model = Keyword
    form_class = KeywordForm
    template_name = 'finance/keyword_form.html'
    success_url = reverse_lazy('keyword_list')

class KeywordUpdateView(UpdateView):
    model = Keyword
    form_class = KeywordForm
    template_name = 'finance/keyword_form.html'
    success_url = reverse_lazy('keyword_list')

class KeywordDeleteView(DeleteView):
    model = Keyword
    template_name = 'finance/keyword_confirm_delete.html'
    success_url = reverse_lazy('keyword_list')




class RecurringTransactionListView(LoginRequiredMixin, ListView):
    model = RecurringTransaction
    template_name = 'finance/recurring_list.html'
    context_object_name = 'recurring_transactions'

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

class RecurringTransactionCreateView(LoginRequiredMixin, CreateView):
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'finance/recurring_form.html'
    success_url = reverse_lazy('recurring_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class RecurringTransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'finance/recurring_form.html'
    success_url = reverse_lazy('recurring_list')

class RecurringTransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = RecurringTransaction
    template_name = 'finance/recurring_confirm_delete.html'
    success_url = reverse_lazy('recurring_list')


@staff_member_required
def recurring_report_view(request):
    year = int(request.GET.get('year', now().year))
    months = range(1, 13)

    # Prepare table data
    data = []
    for template in RecurringTransaction.objects.all().order_by('transaction'):
        row = {
            'template': template,
            'monthly_checks': []
        }
        for month in months:
            target_day = min(template.day, 28)  # Avoid invalid dates
            exists = Transaction.objects.filter(
                recurring_template=template,
                date__year=year,
                date__month=month
            ).exists()
            row['monthly_checks'].append(exists)
        data.append(row)

    return render(request, 'finance/recurring_report.html', {
        'data': data,
        'months': [month_name[m] for m in months],
        'year': year
    })



@staff_member_required
def run_recurring_now_view(request):
    today = now().date()
    created = 0
    skipped = 0

    recurrences = RecurringTransaction.objects.filter(day=today.day, active=True)

    for r in recurrences:
        exists = Transaction.objects.filter(
            user=r.user,
            transaction=r.transaction,
            date__year=today.year,
            date__month=today.month
        ).exists()

        if exists:
            skipped += 1
            continue

        Transaction.objects.create(
            date=today,
            trans_type=r.trans_type,
            category=r.category,
            sub_cat=r.sub_cat,
            amount=r.amount,
            transaction=r.transaction,
            team=r.team,
            keyword=r.keyword,
            tax=r.tax,
            user=r.user,
            paid="Yes"
        )

        created += 1

    messages.success(request, f"{created} transactions created, {skipped} skipped.")
    return redirect('transactions') 


@staff_member_required
def run_monthly_batch_view(request):
    today = now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    last_day = monthrange(year, month)[1]
    created_transactions = []
    skipped = 0
    recurrences = RecurringTransaction.objects.filter(active=True)
    for r in recurrences:
        target_day = min(r.day, last_day)
        trans_date = date(year, month, target_day)
        exists = Transaction.objects.filter(
            recurring_template=r,
            date=trans_date
        ).exists()
        if exists:
            skipped += 1
            continue
        tx = Transaction.objects.create(
            date=trans_date,
            trans_type=r.trans_type,
            category=r.category,
            sub_cat=r.sub_cat,
            amount=r.amount,
            transaction=r.transaction,
            team=r.team,
            keyword=r.keyword,
            tax=r.tax,
            user=r.user,
            paid="Yes",
            recurring_template=r 
        )
        created_transactions.append(tx)
        r.last_created = trans_date
        r.save(update_fields=['last_created'])

    return render(request, 'finance/recurring_batch_success.html', {
        'created': created_transactions,
        'skipped': skipped,
        'run_year': year,
        'run_month': month,
    })

