from django.urls import reverse

def url_names(request):
    return {
        'urls': {
            'transactions': reverse('transactions'),
            'invoice_list': reverse('invoice_list'),
            'mileage_log': reverse('mileage_log'),
            'reports': reverse('reports'),
            'recurring_list': reverse('recurring_list'),
            'category_page': reverse('category_page'),

        }
    }
