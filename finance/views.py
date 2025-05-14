from django.views.generic import TemplateView, ListView, DetailView, UpdateView, DeleteView, CreateView
from django.http import JsonResponse, HttpResponse, StreamingHttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib.postgres.indexes import GinIndex
from django.template.loader import render_to_string
from django.db.models.functions import ExtractYear
from django.template.loader import get_template
from django.urls import reverse_lazy, reverse
from django.core.paginator import Paginator
from django.core.mail import EmailMessage
from django.utils.timezone import now
from django.contrib import messages
from django.db.models import Sum, Q
from collections import defaultdict
from datetime import datetime, date
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from calendar import monthrange
from calendar import month_name
from django.views import View
from weasyprint import HTML
from pathlib import Path
import tempfile
import logging
import csv
import os
from .models import *
from .forms import *


# Dashboard
class Dashboard(LoginRequiredMixin, TemplateView):
    template_name = "finance/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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


# Transactions
class Transactions(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = "finance/transactions.html"
    context_object_name = "transactions"
    paginate_by = 50

    def get_queryset(self):
        queryset = Transaction.objects.select_related(
            'trans_type', 'category', 'sub_cat', 'team', 'keyword'
        ).filter(user=self.request.user)

        # Apply filters
        keyword_id = self.request.GET.get('keyword')
        if keyword_id and Keyword.objects.filter(id=keyword_id).exists():
            queryset = queryset.filter(keyword__id=keyword_id)

        category_id = self.request.GET.get('category')
        if category_id and Category.objects.filter(id=category_id).exists():
            queryset = queryset.filter(category__id=category_id)

        sub_cat_id = self.request.GET.get('sub_cat')
        if sub_cat_id and SubCategory.objects.filter(id=sub_cat_id).exists():
            queryset = queryset.filter(sub_cat__id=sub_cat_id)

        year = self.request.GET.get('year')
        if year and year.isdigit() and 1900 <= int(year) <= 9999:
            queryset = queryset.filter(date__year=year)

        # Apply sorting
        sort = self.request.GET.get('sort', '-date')
        valid_sort_fields = [
            'date', '-date', 'trans_type__trans_type', '-trans_type__trans_type',
            'transaction', '-transaction', 'keyword__name', '-keyword__name',
            'amount', '-amount', 'invoice_numb', '-invoice_numb'
        ]
        if sort in valid_sort_fields:
            queryset = queryset.order_by(sort)
        else:
            queryset = queryset.order_by('-date')

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_sort'] = self.request.GET.get('sort', '-date')
        context['keywords'] = Keyword.objects.filter(transaction__isnull=False, transaction__user=self.request.user).distinct().order_by('name')
        context['categories'] = Category.objects.filter(transaction__isnull=False, transaction__user=self.request.user).distinct().order_by('category')
        context['subcategories'] = SubCategory.objects.filter(transaction__isnull=False, transaction__user=self.request.user).distinct().order_by('sub_cat')
        context['years'] = [str(y) for y in Transaction.objects.filter(user=self.request.user).annotate(
            extracted_year=ExtractYear('date')).values_list('extracted_year', flat=True).distinct().order_by('-extracted_year') if y]
        context['selected_keyword'] = self.request.GET.get('keyword', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['selected_sub_cat'] = self.request.GET.get('sub_cat', '')
        context['selected_year'] = self.request.GET.get('year', '')
        return context


class DownloadTransactionsCSV(LoginRequiredMixin, View):
    def get(self, request):
        transactions_view = Transactions()
        transactions_view.request = request
        queryset = transactions_view.get_queryset()

        class Echo:
            def write(self, value):
                return value
        def stream_csv(queryset):
            writer = csv.writer(Echo())
            yield writer.writerow(['Date', 'Type', 'Transaction', 'Location', 'Amount', 'Invoice #'])
            for tx in queryset.iterator():
                yield writer.writerow([
                    tx.date,
                    tx.trans_type.trans_type if tx.trans_type else '',
                    tx.transaction,
                    tx.keyword.name if tx.keyword else '',
                    tx.amount,
                    tx.invoice_numb
                ])

        try:
            filename = "transactions.csv"
            response = StreamingHttpResponse(stream_csv(queryset), content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
        except Exception as e:
            logger.error(f"Error generating CSV for user {request.user.id}: {e}")
            return HttpResponse("Error generating CSV", status=500)


class TransactionCreateView(LoginRequiredMixin, CreateView):
    model = Transaction
    form_class = TransForm
    template_name = 'finance/transaction_add.html'
    success_url = reverse_lazy('add_transaction_success')

    def form_valid(self, form):
        form.instance.user = self.request.user
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(self.request, 'Transaction added successfully!')
                return response
        except Exception as e:
            logger.error(f"Error adding transaction for user {self.request.user.id}: {e}")
            messages.error(self.request, 'Error adding transaction. Please check the form.')
            return self.form_invalid(form)


class TransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = Transaction
    form_class = TransForm
    template_name = 'finance/transaction_edit.html'
    success_url = reverse_lazy('transactions')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        try:
            with transaction.atomic():
                response = super().form_valid(form)
                messages.success(self.request, 'Transaction updated successfully!')
                return response
        except Exception as e:
            logger.error(f"Error updating transaction {self.get_object().id} for user {self.request.user.id}: {e}")
            messages.error(self.request, 'Error updating transaction. Please check the form.')
            return self.form_invalid(form)


class TransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = Transaction
    template_name = "finance/transaction_confirm_delete.html"
    success_url = reverse_lazy('transactions')

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().delete(request, *args, **kwargs)
                messages.success(self.request, "Transaction deleted successfully!")
                return response
        except models.ProtectedError:
            messages.error(self.request, "Cannot delete transaction due to related records.")
            return redirect('transactions')
        except Exception as e:
            logger.error(f"Error deleting transaction for user {request.user.id}: {e}")
            messages.error(self.request, "Error deleting transaction.")
            return redirect('transactions')


class TransactionDetailView(LoginRequiredMixin, DetailView):
    model = Transaction
    template_name = 'finance/transactions_detail_view.html'
    context_object_name = 'transaction'

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)

def add_transaction_success(request):
    return render(request, 'finance/transaction_add_success.html')


# Invoices
class InvoiceCreateView(LoginRequiredMixin, CreateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'finance/invoice_add.html'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = InvoiceItemFormSet(self.request.POST or None)
        return context

    def form_valid(self, form):
        formset = InvoiceItemFormSet(self.request.POST)
        if formset.is_valid():
            try:
                with transaction.atomic():
                    invoice = form.save(commit=False)
                    invoice.amount = 0
                    invoice.save()
                    for item_form in formset:
                        if item_form.cleaned_data and not item_form.cleaned_data.get('DELETE', False):
                            item = item_form.save(commit=False)
                            item.invoice = invoice
                            item.save()
                    invoice.amount = invoice.items.aggregate(total=Sum('price'))['total'] or 0
                    invoice.save()
                    messages.success(self.request, f"Invoice #{invoice.invoice_numb} created successfully.")
                    return super().form_valid(form)
            except Exception as e:
                logger.error(f"Error creating invoice for user {self.request.user.id}: {e}")
                messages.error(self.request, "Error creating invoice. Please check the form.")
                return self.form_invalid(form)
        else:
            logger.error(f"Formset errors for invoice creation: {formset.errors}")
            messages.error(self.request, "Error in invoice items. Please check the form.")
            return self.form_invalid(form)


class InvoiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Invoice
    form_class = InvoiceForm
    template_name = 'finance/invoice_update.html'
    success_url = reverse_lazy('invoice_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = InvoiceItemFormSet(self.request.POST or None, instance=self.object)
        context['invoice'] = self.object
        return context

    def form_valid(self, form):
        formset = InvoiceItemFormSet(self.request.POST, instance=self.object)
        if formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()
                    invoice = self.object
                    invoice.amount = invoice.items.aggregate(total=Sum('price'))['total'] or 0
                    invoice.save()
                    messages.success(self.request, f"Invoice #{invoice.invoice_numb} updated successfully.")
                    return super().form_valid(form)
            except Exception as e:
                logger.error(f"Error updating invoice {self.object.id} for user {self.request.user.id}: {e}")
                messages.error(self.request, "Error updating invoice. Please check the form.")
                return self.form_invalid(form)
        else:
            logger.error(f"Formset errors for invoice update: {formset.errors}")
            messages.error(self.request, "Error in invoice items. Please check the form.")
            return self.form_invalid(form)


class InvoiceListView(LoginRequiredMixin, ListView):
    model = Invoice
    template_name = "finance/invoices.html"
    context_object_name = "invoices"
    paginate_by = 20

    def get_queryset(self):
        sort = self.request.GET.get('sort', 'invoice_numb')
        direction = self.request.GET.get('direction', 'desc')
        valid_sort_fields = [
            'invoice_numb', 'client__business', 'keyword__name', 'service__service',
            'amount', 'date', 'due', 'paid_date', 'days_to_pay'
        ]
        if sort not in valid_sort_fields:
            sort = 'invoice_numb'
        ordering = f"-{sort}" if direction == 'desc' else sort
        queryset = Invoice.objects.select_related('client', 'keyword', 'service').prefetch_related('items').order_by(ordering)
        search_query = self.request.GET.get('search', '')
        if search_query:
            if len(search_query) > 100:  # Prevent abuse
                search_query = search_query[:100]
            queryset = queryset.filter(
                search_vector=search_query
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

    def get_queryset(self):
        return Invoice.objects.select_related('client', 'keyword', 'service').prefetch_related('items')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logo_path = next((
            os.path.join(path, 'images/logo2.png')
            for path in (settings.STATICFILES_DIRS if hasattr(settings, 'STATICFILES_DIRS') else [])
            if os.path.exists(os.path.join(path, 'images/logo2.png'))
        ), None)
        context['logo_path'] = f'file://{logo_path}' if logo_path and os.path.exists(logo_path) else None
        context['rendering_for_pdf'] = self.request.GET.get('pdf', False)
        return context


class InvoiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Invoice
    template_name = "finance/invoice_confirm_delete.html"
    success_url = reverse_lazy('invoice_list')

    def delete(self, request, *args, **kwargs):
        try:
            with transaction.atomic():
                response = super().delete(request, *args, **kwargs)
                messages.success(self.request, "Invoice deleted successfully.")
                return response
        except models.ProtectedError:
            messages.error(self.request, "Cannot delete invoice due to related records.")
            return redirect('invoice_list')
        except Exception as e:
            logger.error(f"Error deleting invoice for user {request.user.id}: {e}")
            messages.error(self.request, "Error deleting invoice.")
            return redirect('invoice_list')

@login_required
def invoice_review(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    transactions = Transaction.objects.filter(invoice_numb=invoice.invoice_numb).select_related('trans_type')
    totals = transactions.aggregate(
        total_expenses=Sum('amount', filter=Q(trans_type__trans_type='Expense')),
        total_income=Sum('amount', filter=Q(trans_type__trans_type='Income'))
    )
    total_expenses = totals['total_expenses'] or 0
    total_income = totals['total_income'] or 0
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
    invoices = Invoice.objects.filter(paid__iexact="No").select_related('client').order_by('due_date')
    return render(request, 'components/unpaid_invoices.html', {'invoices': invoices})

@login_required
def export_invoices_csv(request):
    invoice_view = InvoiceListView()
    invoice_view.request = request
    queryset = invoice_view.get_queryset()

    class Echo:
        def write(self, value):
            return value
    def stream_csv(queryset):
        writer = csv.writer(Echo())
        yield writer.writerow(['Invoice #', 'Client', 'Location', 'Service', 'Amount', 'Date', 'Due', 'Paid', 'Days to Pay'])
        for invoice in queryset.iterator():
            yield writer.writerow([
                invoice.invoice_numb,
                str(invoice.client),
                invoice.keyword.name if invoice.keyword else '',
                str(invoice.service),
                invoice.amount,
                invoice.date,
                invoice.due,
                invoice.paid_date or "No",
                invoice.days_to_pay if invoice.paid_date else "—"
            ])

    try:
        response = StreamingHttpResponse(stream_csv(queryset), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="invoices.csv"'
        return response
    except Exception as e:
        logger.error(f"Error generating CSV for user {request.user.id}: {e}")
        return HttpResponse("Error generating CSV", status=500)


@login_required
def export_invoices_pdf(request):
    invoice_view = InvoiceListView()
    invoice_view.request = request
    invoices = invoice_view.get_queryset()[:1000]  # Limit to prevent memory issues

    if not invoices.exists():
        messages.error(request, "No invoices to export.")
        return redirect('invoice_list')

    try:
        template = get_template('finance/invoice_pdf_export.html')
        html_string = template.render({'invoices': invoices})
        with tempfile.NamedTemporaryFile(delete=True) as output:
            HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(output.name)
            output.seek(0)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="invoices.pdf"'
            response.write(output.read())
            return response
    except Exception as e:
        logger.error(f"Error generating PDF for user {request.user.id}: {e}")
        messages.error(request, "Error generating PDF.")
        return redirect('invoice_list')


    # Celery example (uncomment if Celery is set up):
    # from celery import shared_task
    # @shared_task
    # def generate_pdf(invoices, base_url):
    #     template = get_template('finance/invoice_pdf_export.html')
    #     html_string = template.render({'invoices': invoices})
    #     with tempfile.NamedTemporaryFile(delete=False) as output:
    #         HTML(string=html_string, base_url=base_url).write_pdf(output.name)
    #         return output.name
    # task = generate_pdf.delay(list(invoices), request.build_absolute_uri())
    # messages.info(request, "PDF generation started.")
    # return redirect('check_task_status', task_id=task.id)


@login_required
def invoice_review_pdf(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    transactions = Transaction.objects.filter(
        invoice_numb=invoice.invoice_numb, trans_type__trans_type__iexact="Expense"
    ).select_related('trans_type')
    total_expenses = transactions.aggregate(total=Sum('amount'))['total'] or 0
    net_amount = invoice.amount - total_expenses

    context = {
        'invoice': invoice,
        'transactions': transactions,
        'invoice_amount': invoice.amount,
        'total_expenses': total_expenses,
        'net_amount': net_amount,
        'now': now(),
    }

    try:
        template = get_template('finance/invoice_review_pdf.html')
        html_string = template.render(context)
        html_string = "<style>@page { size: 8.5in 11in; margin: 1in; }</style>" + html_string

        if request.GET.get("preview") == "1":
            return HttpResponse(html_string)

        with tempfile.NamedTemporaryFile(delete=True) as tmp:
            HTML(string=html_string, base_url=request.build_absolute_uri()).write_pdf(tmp.name)
            tmp.seek(0)
            response = HttpResponse(tmp.read(), content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="invoice_{invoice.invoice_numb}.pdf"'
            return response
    except Exception as e:
        logger.error(f"Error generating PDF for invoice {pk} by user {request.user.id}: {e}")
        messages.error(request, "Error generating PDF.")
        return redirect('invoice_detail', pk=pk)


# Categories
class CategoryListView(LoginRequiredMixin, ListView):
    model = Category
    template_name = 'finance/category_page.html'
    context_object_name = 'category'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['sub_cat'] = SubCategory.objects.order_by('sub_cat')
        return context


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
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, "Category deleted successfully!")
            return response
        except models.ProtectedError:
            messages.error(self.request, "Cannot delete category due to related transactions.")
            return redirect('category_page')
        except Exception as e:
            logger.error(f"Error deleting category for user {request.user.id}: {e}")
            messages.error(self.request, "Error deleting category.")
            return redirect('category_page')


# ------------------------------------------------------------------------------------------ Sub-Categories

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
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, "Sub-Category deleted successfully!")
            return response
        except models.ProtectedError:
            messages.error(self.request, "Cannot delete sub-category due to related transactions.")
            return redirect('category_page')
        except Exception as e:
            logger.error(f"Error deleting sub-category for user {request.user.id}: {e}")
            messages.error(self.request, "Error deleting sub-category.")
            return redirect('category_page')


# ---------------------------------------------------------------------------------------Clients
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
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, "Client deleted successfully!")
            return response
        except models.ProtectedError:
            messages.error(self.request, "Cannot delete client due to related invoices.")
            return redirect('client_list')
        except Exception as e:
            logger.error(f"Error deleting client for user {request.user.id}: {e}")
            messages.error(self.request, "Error deleting client.")
            return redirect('client_list')


# -------------------------------------------------------------------------------------------Financial Reports

def get_summary_data(request, year):
    current_year = timezone.now().year
    try:
        year = int(year) if year and year.isdigit() else current_year
        if year < 1900 or year > 9999:
            year = current_year
            messages.error(request, "Invalid year selected.")
    except ValueError:
        year = current_year
        messages.error(request, "Invalid year selected.")

    # Base queryset for transactions
    transactions = Transaction.objects.filter(
        user=request.user, date__year=year, trans_type__isnull=False
    ).select_related('trans_type', 'category', 'sub_cat')

    # Income and expense querysets
    income_qs = transactions.filter(trans_type__trans_type='Income')
    expense_qs = transactions.filter(trans_type__trans_type='Expense')

    # Category and subcategory totals
    income_category_totals = income_qs.values('category__category').annotate(total=Sum('amount')).order_by('category__category')
    expense_category_totals = expense_qs.values('category__category').annotate(total=Sum('amount')).order_by('category__category')
    income_subcategory_totals = income_qs.values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('sub_cat__sub_cat')
    expense_subcategory_totals = expense_qs.values('sub_cat__sub_cat').annotate(total=Sum('amount')).order_by('sub_cat__sub_cat')

    # Total income and expense
    income_category_total = income_qs.aggregate(total=Sum('amount'))['total'] or 0
    expense_category_total = expense_qs.aggregate(total=Sum('amount'))['total'] or 0

    # Net profit
    net_profit = income_category_total - expense_category_total

    # Available years for dropdown (optional, based on template)
    available_years = Transaction.objects.filter(user=request.user).dates('date', 'year')

    return {
        'selected_year': year,
        'income_category_totals': income_category_totals,
        'expense_category_totals': expense_category_totals,
        'income_subcategory_totals': income_subcategory_totals,
        'expense_subcategory_totals': expense_subcategory_totals,
        'income_category_total': income_category_total,
        'expense_category_total': expense_category_total,
        'net_profit': net_profit,
        'available_years': available_years,
    }

@login_required
def financial_statement(request):
    current_year = timezone.now().year
    year = request.GET.get('year', str(current_year))
    context = get_summary_data(request, year)
    context['available_years'] = [d.year for d in Transaction.objects.filter(
        user=request.user).dates('date', 'year', order='DESC').distinct()]
    return render(request, 'finance/financial_statement.html', context)


@login_required
def category_summary(request):
    current_year = timezone.now().year
    year = request.GET.get('year', str(current_year))
    context = get_summary_data(request, year)
    context['available_years'] = [d.year for d in Transaction.objects.filter(
        user=request.user).dates('date', 'year', order='DESC').distinct()]
    return render(request, 'finance/category_summary.html', context)


@login_required
def print_category_summary(request):
    year = request.GET.get('year', str(timezone.now().year))
    context = get_summary_data(request, year)
    return render(request, 'finance/category_summary_print.html', context)


@login_required
def nhra_summary(request):
    current_year = timezone.now().year
    years = [current_year, current_year - 1, current_year - 2]
    excluded_ids = [35, 133, 34, 67, 100]

    summary_data = Transaction.objects.filter(
        user=request.user
    ).exclude(keyword__id__in=excluded_ids).filter(
        date__year__in=years, trans_type__isnull=False
    ).values('keyword__name', 'date__year', 'trans_type__trans_type').annotate(
        total=Sum('amount')
    ).order_by('keyword__name', 'date__year')

    result = defaultdict(lambda: {y: {"income": 0, "expense": 0, "net": 0} for y in years})
    for item in summary_data:
        keyword = item['keyword__name']
        year = item['date__year']
        trans_type = item['trans_type__trans_type'].lower()
        result[keyword][year][trans_type] = item['total']
        result[keyword][year]['net'] = result[keyword][year]['income'] - result[keyword][year]['expense']

    return render(request, "finance/nhra_summary.html", {
        "years": years,
        "summary_data": result,
    })


@login_required
def reports_page(request):
    return render(request, 'finance/reports.html')


# Emails
@require_POST
@login_required
def send_invoice_email(request, invoice_id):
    invoice = get_object_or_404(Invoice, pk=invoice_id)
    try:
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
        if not invoice.client.email and not hasattr(settings, 'DEFAULT_EMAIL'):
            raise ValueError("No valid email address provided.")
        email = EmailMessage(subject, body, from_email, recipient)
        email.content_subtype = 'html'
        email.attach(f"Invoice_{invoice.invoice_numb}.pdf", pdf_file, "application/pdf")
        email.send()
        return JsonResponse({'status': 'success', 'message': 'Invoice emailed successfully!'})
    except Exception as e:
        logger.error(f"Error sending email for invoice {invoice_id} by user {request.user.id}: {e}")
        return JsonResponse({'status': 'error', 'message': 'Failed to send email'}, status=500)


    # Celery example (uncomment if Celery is set up):
    # from celery import shared_task
    # @shared_task
    # def send_invoice_email_task(invoice_id, base_url):
    #     invoice = Invoice.objects.get(pk=invoice_id)
    #     html_string = render_to_string('finance/invoice_detail.html', {'invoice': invoice})
    #     html = HTML(string=html_string, base_url=base_url)
    #     pdf_file = html.write_pdf()
    #     email = EmailMessage(...)
    #     email.send()
    # task = send_invoice_email_task.delay(invoice_id, request.build_absolute_uri())
    # return JsonResponse({'status': 'queued', 'task_id': task.id})


# -----------------------------------------------------------------------------------------------------------Mileage

def get_mileage_context(request):
    try:
        rate = MileageRate.objects.first().rate if MileageRate.objects.exists() else 0.70
    except Exception as e:
        logger.error(f"Error fetching mileage rate: {e}")
        rate = 0.70
        messages.error(request, "Error fetching mileage rate. Using default rate.")

    year = datetime.now().year
    entries = Miles.objects.filter(user=request.user, date__year=year)
    paginator = Paginator(entries, 50)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    taxable = entries.filter(mileage_type='Taxable')
    total_miles = taxable.aggregate(Sum('total'))['total__sum'] or 0

    return {
        'mileage_list': page_obj,
        'page_obj': page_obj,
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
        messages.success(self.request, "Mileage entry added successfully!")
        return super().form_valid(form)


class MileageUpdateView(LoginRequiredMixin, UpdateView):
    model = Miles
    form_class = MileageForm
    template_name = 'finance/mileage_form.html'
    success_url = reverse_lazy('mileage_log')

    def get_queryset(self):
        return Miles.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Mileage entry updated successfully!")
        return super().form_valid(form)


class MileageDeleteView(LoginRequiredMixin, DeleteView):
    model = Miles
    template_name = 'finance/mileage_confirm_delete.html'
    success_url = reverse_lazy('mileage_log')

    def get_queryset(self):
        return Miles.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Mileage entry deleted successfully!")
        return super().delete(request, *args, **kwargs)


@login_required
def update_mileage_rate(request):
    mileage_rate = MileageRate.objects.first() or MileageRate(rate=0.70)
    if request.method == 'POST':
        form = MileageRateForm(request.POST, instance=mileage_rate)
        if form.is_valid():
            form.save()
            messages.success(request, "Mileage rate updated successfully!")
            return redirect('mileage_log')
        else:
            messages.error(request, "Error updating mileage rate. Please check the form.")
    else:
        form = MileageRateForm(instance=mileage_rate)
    return render(request, 'components/update_mileage_rate.html', {'form': form})


# ---------------------------------------------------------------------------------------------------Keywords
class KeywordListView(LoginRequiredMixin, ListView):
    model = Keyword
    template_name = 'finance/keyword_list.html'
    context_object_name = 'keywords'


class KeywordCreateView(LoginRequiredMixin, CreateView):
    model = Keyword
    form_class = KeywordForm
    template_name = 'finance/keyword_form.html'
    success_url = reverse_lazy('keyword_list')

    def form_valid(self, form):
        messages.success(self.request, "Keyword added successfully!")
        return super().form_valid(form)


class KeywordUpdateView(LoginRequiredMixin, UpdateView):
    model = Keyword
    form_class = KeywordForm
    template_name = 'finance/keyword_form.html'
    success_url = reverse_lazy('keyword_list')

    def form_valid(self, form):
        messages.success(self.request, "Keyword updated successfully!")
        return super().form_valid(form)


class KeywordDeleteView(LoginRequiredMixin, DeleteView):
    model = Keyword
    template_name = 'finance/keyword_confirm_delete.html'
    success_url = reverse_lazy('keyword_list')

    def delete(self, request, *args, **kwargs):
        try:
            response = super().delete(request, *args, **kwargs)
            messages.success(self.request, "Keyword deleted successfully!")
            return response
        except models.ProtectedError:
            messages.error(self.request, "Cannot delete keyword due to related transactions.")
            return redirect('keyword_list')
        except Exception as e:
            logger.error(f"Error deleting keyword for user {request.user.id}: {e}")
            messages.error(self.request, "Error deleting keyword.")
            return redirect('keyword_list')


# ------------------------------------------------------------------------------------------------Recurring Transactions

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
        messages.success(self.request, "Recurring transaction added successfully!")
        return super().form_valid(form)


class RecurringTransactionUpdateView(LoginRequiredMixin, UpdateView):
    model = RecurringTransaction
    form_class = RecurringTransactionForm
    template_name = 'finance/recurring_form.html'
    success_url = reverse_lazy('recurring_list')

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, "Recurring transaction updated successfully!")
        return super().form_valid(form)


class RecurringTransactionDeleteView(LoginRequiredMixin, DeleteView):
    model = RecurringTransaction
    template_name = 'finance/recurring_confirm_delete.html'
    success_url = reverse_lazy('recurring_list')

    def get_queryset(self):
        return RecurringTransaction.objects.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, "Recurring transaction deleted successfully!")
        return super().delete(request, *args, **kwargs)


@staff_member_required
def recurring_report_view(request):
    year = int(request.GET.get('year', now().year))
    months = range(1, 13)
    templates = RecurringTransaction.objects.filter(user=request.user).order_by('transaction')
    transactions = Transaction.objects.filter(
        recurring_template__in=templates, date__year=year
    ).values('recurring_template_id', 'date__month').distinct()
    existence_map = {(t['recurring_template_id'], t['date__month']): True for t in transactions}

    data = []
    for template in templates:
        row = {
            'template': template,
            'monthly_checks': [existence_map.get((template.id, month), False) for month in months]
        }
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

    try:
        with transaction.atomic():
            recurrences = RecurringTransaction.objects.filter(day=today.day, active=True, user=request.user)
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
    except Exception as e:
        logger.error(f"Error running recurring transactions for user {request.user.id}: {e}")
        messages.error(request, "Error running recurring transactions.")
        return redirect('transactions')


@staff_member_required
def run_monthly_batch_view(request):
    today = now().date()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))
    last_day = monthrange(year, month)[1]
    created_transactions = []
    skipped = 0

    try:
        with transaction.atomic():
            recurrences = RecurringTransaction.objects.filter(active=True, user=request.user)
            transactions_to_create = []
            for r in recurrences:
                target_day = min(r.day, last_day)
                trans_date = date(year, month, target_day)
                exists = Transaction.objects.filter(
                    recurring_template=r, date=trans_date
                ).exists()
                if exists:
                    skipped += 1
                    continue
                tx = Transaction(
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
                transactions_to_create.append(tx)
                r.last_created = trans_date
            Transaction.objects.bulk_create(transactions_to_create)
            RecurringTransaction.objects.filter(
                id__in=[r.id for r in recurrences if r.last_created == trans_date]
            ).update(last_created=trans_date)
            created_transactions = transactions_to_create
    except Exception as e:
        logger.error(f"Error running batch for user {request.user.id}: {e}")
        messages.error(request, "Error running batch.")
        return redirect('recurring_report')

    return render(request, 'finance/recurring_batch_success.html', {
        'created': created_transactions,
        'skipped': skipped,
        'run_year': year,
        'run_month': month,
    })


    # Celery example (uncomment if Celery is set up):
    # from celery import shared_task
    # @shared_task
    # def run_monthly_batch(year, month, user_id):
    #     ... (same logic as above)
    #     return {'created': len(created_transactions), 'skipped': skipped}
    # task = run_monthly_batch.delay(year, month, request.user.id)
    # messages.info(request, "Batch processing started.")
    # return redirect('check_task_status', task_id=task.id)