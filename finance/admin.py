from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *



class CategoryAdmin(admin.ModelAdmin):
    list_display    = ['category']
    
class TransactionAdmin(admin.ModelAdmin):
    list_display    = ['date', 'sub_cat', 'amount', 'invoice_numb']

class GroupAdmin(admin.ModelAdmin):
    list_display    = ['name', 'date']
    

admin.site.register(InvoiceItem)
admin.site.register(MileageRate)
admin.site.register(Client)
admin.site.register(Keyword)
admin.site.register(Type)
admin.site.register(Invoice)
admin.site.register(Service)
admin.site.register(Team)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Miles)