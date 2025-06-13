from django.urls import reverse_lazy

def navigation(request):
    return {
        'finance_navigation': {  # Changed from 'navigation'
            'dashboard': reverse_lazy('dashboard'),
            'transactions': reverse_lazy('transactions'),
            'invoices': reverse_lazy('invoice_list'),
            'mileage': reverse_lazy('mileage_log'),
            'categories': reverse_lazy('category_page'),
            'reports': reverse_lazy('reports'),
            'keywords': reverse_lazy('keyword_list'),
            'recurring transactions': reverse_lazy('recurring_transaction_list'),
            'recurring report': reverse_lazy('recurring_report'),
        }
    }