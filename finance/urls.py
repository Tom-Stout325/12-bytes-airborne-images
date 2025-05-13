from django.urls import path
from .views import (
    Dashboard, Transactions, DownloadTransactionsCSV,
    add_transaction, add_transaction_success, edit_transaction, transaction_detail_page,
    TransactionDeleteView, transaction_delete, transaction_search, download_transactions,
    InvoiceListView, invoice_review, invoice_review_pdf, InvoiceDetailView,
    create_invoice, create_invoice_success, update_invoice, send_invoice_email,
    invoice_delete, unpaid_invoices, export_invoices_csv, export_invoices_pdf,
    CategoryCreateView, CategoryUpdateView, CategoryDeleteView,
    SubCategoryCreateView, SubCategoryUpdateView, SubCategoryDeleteView,
    ClientListView, ClientCreateView, ClientUpdateView, ClientDeleteView,
    reports_page, financial_statement, category_page,
    category_summary, print_category_summary, nhra_summary,
    mileage_log, MileageCreateView, MileageUpdateView, MileageDeleteView, update_mileage_rate,
    KeywordListView, KeywordCreateView, KeywordUpdateView, KeywordDeleteView,
    RecurringTransactionListView, RecurringTransactionCreateView, RecurringTransactionUpdateView,
    RecurringTransactionDeleteView, run_recurring_now_view, run_monthly_batch_view, recurring_report_view
)

urlpatterns = [
    # Dashboard
    path('dashboard', Dashboard.as_view(), name='dashboard'),

    # Transactions
    path('transactions/', Transactions.as_view(), name="transactions"),
    path('transactions/download/', DownloadTransactionsCSV.as_view(), name="download_transactions_csv"),
    path('transaction/new', add_transaction, name="add_transaction"),
    path('transaction/success', add_transaction_success, name='add_transaction_success'),
    path('transaction/<int:pk>/', transaction_detail_page, name='transaction_detail'),
    path('transaction/edit/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
    path('transaction/delete/<int:pk>/', TransactionDeleteView.as_view(), name='delete_transaction'),
    path('transactions/<int:pk>/delete/', transaction_delete, name='transaction_delete'),
    path('transactions-search/', transaction_search, name='transactions_search'),
    path('download_transactions/', download_transactions, name='download_transactions'),
    path('transactions/run-monthly-batch/', run_monthly_batch_view, name='run_monthly_batch'),

    # Invoices
    path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
    path('invoices/<int:pk>/delete/', invoice_delete, name='invoice_delete'),
    path('invoice/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
    path('invoice/<int:pk>/review/', invoice_review, name='invoice_review'),
    path('invoice/<int:pk>/pdf/', invoice_review_pdf, name='invoice_review_pdf'),
    path('invoice/new', create_invoice, name='create_invoice'),
    path('invoice/success', create_invoice_success, name='create_invoice_success'),
    path('invoice/edit/<int:pk>/', update_invoice, name='update_invoice'),
    path('invoice/<int:invoice_id>/email/', send_invoice_email, name='send_invoice_email'),
    path('unpaid-invoices/', unpaid_invoices, name='unpaid_invoices'),
    path('invoices/export/csv/', export_invoices_csv, name='export_invoices_csv'),
    path('invoices/export/pdf/', export_invoices_pdf, name='export_invoices_pdf'),

    # Categories & Subcategories
    path('category-report/', category_page, name='category_page'),
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

    # Mileage
    path('mileage-log/', mileage_log, name='mileage_log'),
    path('mileage/add/', MileageCreateView.as_view(), name='mileage_create'),
    path('mileage/<int:pk>/edit/', MileageUpdateView.as_view(), name='mileage_update'),
    path('mileage/<int:pk>/delete/', MileageDeleteView.as_view(), name='mileage_delete'),
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
