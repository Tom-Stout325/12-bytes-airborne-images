from django.urls import path
from .views import (
    Dashboard, Transactions, DownloadTransactionsCSV,
    TransactionCreateView, TransactionUpdateView, TransactionDetailView, TransactionDeleteView,
    add_transaction_success,
    InvoiceListView, invoice_review, invoice_review_pdf, InvoiceDetailView,
    InvoiceCreateView, InvoiceUpdateView, InvoiceDeleteView, send_invoice_email,
    unpaid_invoices, export_invoices_csv, export_invoices_pdf,
    CategoryListView, CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    SubCategoryCreateView, SubCategoryUpdateView, SubCategoryDeleteView,
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    reports_page, financial_statement, category_summary, print_category_summary, nhra_summary,
    mileage_log, MileageCreateView, MileageUpdateView, MileageDeleteView, update_mileage_rate,
    KeywordListView, KeywordCreateView, KeywordUpdateView, KeywordDeleteView,
    RecurringTransactionListView, RecurringTransactionCreateView, RecurringTransactionUpdateView,
    RecurringTransactionDeleteView, run_recurring_now_view, run_monthly_batch_view, recurring_report_view, 
    travel_expense_report, travel_expense_report_pdf
)

urlpatterns = [
    # Dashboard
    path('dashboard', Dashboard.as_view(), name='dashboard'),

    # Transactions
    path('transactions/', Transactions.as_view(), name="transactions"),
    path('transactions/download/', DownloadTransactionsCSV.as_view(), name="download_transactions_csv"),
    path('transaction/new', TransactionCreateView.as_view(), name="add_transaction"),
    path('transaction/success', add_transaction_success, name='add_transaction_success'),
    path('transaction/<int:pk>/', TransactionDetailView.as_view(), name='transaction_detail'),
    path('transaction/edit/<int:pk>/', TransactionUpdateView.as_view(), name='edit_transaction'),
    path('transaction/delete/<int:pk>/', TransactionDeleteView.as_view(), name='delete_transaction'),
    path('transactions/run-monthly-batch/', run_monthly_batch_view, name='run_monthly_batch'),

    # Invoices
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/delete/', InvoiceDeleteView.as_view(), name='invoice_delete'),
    path('invoice/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoice/<int:pk>/review/', invoice_review, name='invoice_review'),
    path('invoice/<int:pk>/pdf/', invoice_review_pdf, name='invoice_review_pdf'),
    path('invoice/new', InvoiceCreateView.as_view(), name='create_invoice'),
    path('invoice/edit/<int:pk>/', InvoiceUpdateView.as_view(), name='update_invoice'),
    path('invoice/<int:invoice_id>/email/', send_invoice_email, name='send_invoice_email'),
    path('unpaid-invoices/', unpaid_invoices, name='unpaid_invoices'),
    path('invoices/export/csv/', export_invoices_csv, name='export_invoices_csv'),
    path('invoices/export/pdf/', export_invoices_pdf, name='export_invoices_pdf'),

    # Categories & Subcategories
    path('category-report/', CategoryListView.as_view(), name='category_page'),
    path('category/add/', CategoryCreateView.as_view(), name='add_category'),
    path('category/edit/<int:pk>/', CategoryUpdateView.as_view(), name='edit_category'),
    path('category/delete/<int:pk>/', CategoryDeleteView.as_view(), name='delete_category'),
    path('sub_category/add/', SubCategoryCreateView.as_view(), name='add_sub_category'),
    path('sub_category/edit/<int:pk>/', SubCategoryUpdateView.as_view(), name='edit_sub_category'),
    path('sub_category/delete/<int:pk>/', SubCategoryDeleteView.as_view(), name='delete_sub_category'),

    # Clients
    path('clients/', ClientListView.as_view(), name='client_list'),
    path('clients/add/', ClientCreateView.as_view(), name='add_client'),
    path('clients/edit/<int:pk>/', ClientUpdateView.as_view(), name='edit_client'),
    path('client/delete/<int:pk>/', ClientDeleteView.as_view(), name='delete_client'),

    # Reports
    path('reports/', reports_page, name='reports'),
    path('financial-statement/', financial_statement, name='financial_statement'),
    path('category-summary/', category_summary, name='category_summary'),
    path('print-category-summary/', print_category_summary, name='print_category_summary'),
    path('nhra-summary/', nhra_summary, name='nhra_summary'),
    path('travel-expense-report/', travel_expense_report, name='travel_expense_report'),
    path('travel-expense-report/pdf/', travel_expense_report_pdf, name='travel_expense_report_pdf'),
    
    # Mileage
    path('mileage-log/', mileage_log, name='mileage_log'),
    path('mileage/add/', MileageCreateView.as_view(), name='mileage_create'),
    path('mileage/<int:pk>/edit/', MileageUpdateView.as_view(), name='mileage_update'),
    path('mileage/<int:pk>/delete/', MileageDeleteView.as_view(), name='mileage_update'),
    path('mileage/update-rate/', update_mileage_rate, name='update_mileage_rate'),

    # Keywords
    path('keywords/', KeywordListView.as_view(), name='keyword_list'),
    path('keywords/add/', KeywordCreateView.as_view(), name='keyword_create'),
    path('keywords/<int:pk>/edit/', KeywordUpdateView.as_view(), name='keyword_update'),
    path('keywords/<int:pk>/delete/', KeywordDeleteView.as_view(), name='keyword_delete'),

    # Recurring
    path('recurring/', RecurringTransactionListView.as_view(), name='recurring_list'),
    path('recurring/add/', RecurringTransactionCreateView.as_view(), name='recurring_add'),
    path('recurring/<int:pk>/edit/', RecurringTransactionUpdateView.as_view(), name='recurring_edit'),
    path('recurring/<int:pk>/delete/', RecurringTransactionDeleteView.as_view(), name='recurring_delete'),
    path('run-recurring-now/', run_recurring_now_view, name='run_recurring_now'),
    path('recurring/report/', recurring_report_view, name='recurring_report'),
]