from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *


urlpatterns = [
  path('dashboard', Dashboard.as_view(), name="dashboard"),

  path('transactions', Transactions.as_view(), name="transactions"),
  path('transaction/<int:pk>/', transaction_detail_page, name='transaction_detail'),
  path('transaction/new', add_transaction, name="add_transaction"),
  path('transaction/success', add_transaction_success, name='add_transaction_success'),    
  path('transaction/delete/<int:pk>/', TransactionDeleteView.as_view(), name='delete_transaction'),
  path('transaction/edit/<int:transaction_id>/', edit_transaction, name='edit_transaction'),
  path('download_transactions/', download_transactions, name='download_transactions'),

  path('invoices/', InvoiceListView.as_view(), name='invoice_list'),
  path('invoice/<int:pk>/review/', invoice_review, name='invoice_review'),
  path('invoice/<int:pk>/', InvoiceDetailView.as_view(), name='invoice_detail'),
  path('invoice/new', create_invoice, name="create_invoice"),
  path('unpaid-invoices/', unpaid_invoices, name="unpaid_invoices"),
  path('invoice/edit/<int:pk>/', update_invoice, name='update_invoice'),
  path('invoice/success', create_invoice_success, name='create_invoice_success'),    
  path('invoice/<int:invoice_id>/email/', send_invoice_email, name='send_invoice_email'),

  path('categories/', CategoryListView.as_view(), name='category_list'),
  path('category/add/', CategoryCreateView.as_view(), name='add_category'),
  path('category/edit/<int:pk>/', CategoryUpdateView.as_view(), name='edit_category'),
  path('category/delete/<int:pk>/',CategoryDeleteView.as_view(), name='delete_category'),

  path('sub_categories/', SubCategoryListView.as_view(), name='sub_category_list'),
  path('sub_category/add/', SubCategoryCreateView.as_view(), name='add_sub_category'),
  path('sub_category/edit/<int:pk>/', SubCategoryUpdateView.as_view(), name='edit_sub_category'),
  path('sub_category/delete/<int:pk>/',SubCategoryDeleteView.as_view(), name='delete_sub_category'),

  path('clients/', ClientListView.as_view(), name='client_list'),
  path('clients/add/', ClientCreateView.as_view(), name='add_client'),
  path('clients/edit/<int:pk>/', ClientUpdateView.as_view(), name='edit_client'),
  path('client/delete/<int:pk>/',ClientDeleteView.as_view(), name='delete_client'),

  path('financial-statement/', financial_statement, name='financial_statement'),
  path('category-summary/', category_summary, name='category_summary'),
  path('print-category-summary/', print_category_summary, name='print_category_summary'),
  path('keyword-financial-summary/', keyword_financial_summary, name='keyword_financial_summary'),

  path('mileage/', mileage_list, name='mileage_list'),
  path('mileage/add/', MileageCreateView.as_view(), name='mileage_create'),
  path('mileage/<int:pk>/edit/', MileageUpdateView.as_view(), name='mileage_update'),
  path('mileage/<int:pk>/delete/', MileageDeleteView.as_view(), name='mileage_delete'),
  path('mileage/update-rate/', update_mileage_rate, name='update_mileage_rate'),
  
]
