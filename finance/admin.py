from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *



    
class TransactionAdmin(admin.ModelAdmin):
    list_display    = ['date', 'category', 'sub_cat', 'transaction', 'keyword', 'invoice_numb']


class GroupAdmin(admin.ModelAdmin):
    list_display    = ['name', 'date']
    

class TeamAdmin(admin.ModelAdmin):
    list_display    = ['name', 'id']
    
    
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_numb', 'client', 'amount', 'status', 'paid_date', 'days_to_pay')

    def days_to_pay(self, obj):
        return obj.days_to_pay if obj.days_to_pay is not None else "-"
    days_to_pay.short_description = "Days to Pay"


class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category', 'id', 'schedule_c_line']
    search_fields = ('category',)


class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ['sub_cat', 'id', 'category']
    

class RecurringTransactionAdmin(admin.ModelAdmin):
    list_display = ('transaction', 'id', 'amount', 'day', 'category', 'sub_cat', 'user', 'active', 'last_created')
    list_filter = ('active', 'day', 'category', 'sub_cat')
    search_fields = ('transaction', 'user__username')

class KeywordAdmin(admin.ModelAdmin):
    list_display = ['name', 'id']
    


admin.site.register(InvoiceItem)
admin.site.register(MileageRate)
admin.site.register(Client)
admin.site.register(Keyword, KeywordAdmin)
admin.site.register(Service)
admin.site.register(Team, TeamAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(SubCategory, SubCategoryAdmin)
admin.site.register(Transaction, TransactionAdmin)
admin.site.register(Miles)
admin.site.register(RecurringTransaction, RecurringTransactionAdmin)
admin.site.register(Invoice, InvoiceAdmin)