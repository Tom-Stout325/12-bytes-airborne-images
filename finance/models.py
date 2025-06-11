from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.auth.models import User
from datetime import timedelta, date
from decimal import Decimal
from django.conf import settings
try:
    from django.contrib.postgres.indexes import GinIndex
    from django.contrib.postgres.search import SearchVectorField
except ImportError:
    GinIndex = None
    SearchVectorField = None


class Type(models.Model):
    trans_type = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Types"

    def __str__(self):
        return self.trans_type


class Category(models.Model):
    category = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
         verbose_name_plural = "Categories"

    def __str__(self):
        return self.category


class SubCategory(models.Model):
    sub_cat = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Sub Categories"
 
    def __str__(self):
        return self.sub_cat


class Keyword(models.Model):
    name       = models.CharField(max_length=500)
    order      = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Team(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
   
    def __str__(self):
        return self.name

class Client(models.Model):
    business  = models.CharField(max_length=500, blank=True, null=True)
    first     = models.CharField(max_length=500, blank=True, null=True)
    last      = models.CharField(max_length=500, blank=True, null=True)
    street    = models.CharField(max_length=500, blank=True, null=True)
    address2  = models.CharField(max_length=500, blank=True, null=True)
    email     = models.EmailField(max_length=254)
    phone     = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.business
    
class Service(models.Model):
    service = models.CharField(max_length=500, blank=True, null=True) 
    
    def __str__(self):
        return self.service
    
class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trans_type = models.ForeignKey('Type', on_delete=models.PROTECT)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    sub_cat = models.ForeignKey('SubCategory', on_delete=models.PROTECT, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    transaction = models.CharField(max_length=255)
    team = models.ForeignKey('Team', null=True, blank=True, on_delete=models.PROTECT)
    keyword = models.ForeignKey('Keyword', null=True, blank=True, on_delete=models.PROTECT)
    tax = models.CharField(max_length=10, default="Yes")
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateField()
    invoice_numb = models.CharField(max_length=255, blank=True, null=True)
    recurring_template = models.ForeignKey(
        'RecurringTransaction',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='transactions' 
        )

    class Meta:
        indexes = [
            models.Index(fields=['date', 'trans_type']),
            models.Index(fields=['user', 'date']),
            models.Index(fields=['keyword']),
            models.Index(fields=['category']),
            models.Index(fields=['sub_cat']),
            models.Index(fields=['invoice_numb']),
        ]
        verbose_name_plural = "Transactions"
        ordering = ['date']
        
    @property
    def deductible_amount(self):
        if self.sub_cat_id == 26:
            return round(self.amount * 0.5, 2)
        return self.amount


    def __str__(self):
        return f"{self.transaction} - {self.amount}"
    
    def save(self, *args, **kwargs):
        if self.sub_cat_id == 26:
            self.deductible_amount = round(Decimal(self.amount) * Decimal('0.5'), 2)
        else:
            self.deductible_amount = None 
        super().save(*args, **kwargs)


class Invoice(models.Model):
    invoice_numb = models.CharField(max_length=10, unique=True)
    client = models.ForeignKey('Client', on_delete=models.PROTECT)
    event = models.CharField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)
    keyword = models.ForeignKey('Keyword', on_delete=models.PROTECT, default=1)
    service = models.ForeignKey('Service', on_delete=models.PROTECT)
    amount = models.DecimalField(default=0.00, max_digits=12, decimal_places=2)
    date = models.DateField() 
    due = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid'), ('Partial', 'Partial')],
        default='Unpaid'
    )
    search_vector = SearchVectorField(null=True, blank=True) if SearchVectorField else None

    class Meta:
        indexes = [
            models.Index(fields=['invoice_numb']),
            models.Index(fields=['date']),
            models.Index(fields=['due']),
            models.Index(fields=['paid_date']),
            models.Index(fields=['client']),
            models.Index(fields=['keyword']),
            models.Index(fields=['service']),
        ]
        if GinIndex and 'django.contrib.postgres' in settings.INSTALLED_APPS:
            indexes.append(
                GinIndex(fields=['search_vector'], name='invoice_search_idx')
            )
        ordering = ['invoice_numb']

    def __str__(self):
        return self.invoice_numb

    def calculate_total(self):
        return sum(item.total for item in self.items.all())

    @property
    def is_paid(self):
        return self.paid_date is not None

    @property
    def days_to_pay(self):
        if self.paid_date:
            return (self.paid_date - self.date).days
        return None


class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Service, on_delete=models.PROTECT, blank=True, null=True)
    qty = models.IntegerField(default=0, blank=True, null=True)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00, blank=True, null=True)

    def __str__(self):
        return f"{self.item.service if self.item else 'No Item'} - {self.qty} x {self.price}"

    @property
    def total(self):
        return (self.qty or 0) * (self.price or 0)




class MileageRate(models.Model):
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.70)
    
    def __str__(self):
        return f"Current Mileage Rate: ${self.rate}"

    class Meta:
        verbose_name = "Mileage Rate"
        verbose_name_plural = "Mileage Rates"



class Miles(models.Model):
    MILEAGE_TYPE_CHOICES = [
        ('Taxable', 'Taxable'),
        ('Reimbursed', 'Reimbursed'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    begin = models.DecimalField(max_digits=10, decimal_places=1, null=True, validators=[MinValueValidator(0)])
    end = models.DecimalField(max_digits=10, decimal_places=1, null=True, validators=[MinValueValidator(0)])
    total = models.DecimalField(max_digits=10, decimal_places=1, null=True, editable=False)
    client = models.ForeignKey('Client', on_delete=models.PROTECT)
    invoice = models.CharField(max_length=255, blank=True, null=True)
    tax = models.CharField(max_length=10, blank=False, null=True, default="Yes")
    job = models.CharField(max_length=255, blank=True, null=True)
    vehicle = models.CharField(max_length=255, blank=False, null=True, default="Lead Foot")
    mileage_type = models.CharField(max_length=20, choices=MILEAGE_TYPE_CHOICES, default='Taxable')

    class Meta:
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['mileage_type']),
        ]
        verbose_name_plural = "Miles"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.client}"

    def save(self, *args, **kwargs):
        if self.begin is not None and self.end is not None:
            self.total = round(self.end - self.begin, 1)
        else:
            self.total = None
        super().save(*args, **kwargs)


class RecurringTransaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    trans_type = models.ForeignKey('Type', on_delete=models.PROTECT)
    category = models.ForeignKey('Category', on_delete=models.PROTECT)
    sub_cat = models.ForeignKey('SubCategory', on_delete=models.PROTECT, null=True, blank=True)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    transaction = models.CharField(max_length=255)
    day = models.IntegerField(help_text="Day of the month to apply")
    team = models.ForeignKey('Team', null=True, on_delete=models.PROTECT, blank=True)
    keyword = models.ForeignKey('Keyword', null=True, on_delete=models.PROTECT, blank=True)
    tax = models.CharField(max_length=10, default="Yes")
    receipt = models.FileField(upload_to='receipts/', blank=True, null=True)
    account = models.CharField(max_length=255, blank=True, null=True)
    active = models.BooleanField(default=True)
    last_created = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.transaction} - {self.amount} on day {self.day}"

    class Meta:
        indexes = [models.Index(fields=['user', 'day', 'active'])]
