from django.db import models
from django.core.validators import MinValueValidator



class Type(models.Model):
    trans_type        = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Types"

    def __str__(self):
        return self.trans_type

# -------------------------------------------------------------------------------------------

class Category(models.Model):
    category        = models.CharField(max_length=500, blank=True, null=True)
    
    class Meta:
         verbose_name_plural = "Categories"

    def __str__(self):
        return self.category

# -------------------------------------------------------------------------------------------

class SubCategory(models.Model):
    sub_cat = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        verbose_name_plural = "Sub Categories"
 
    def __str__(self):
        return self.sub_cat

# -------------------------------------------------------------------------------------------

class Keyword(models.Model):
    name            = models.CharField(max_length=500)

    def __str__(self):
        return self.name

# -------------------------------------------------------------------------------------------

class Team(models.Model):
    name                    = models.CharField(max_length=50, blank=True, null=True)
   
    def __str__(self):
        return self.name

# -------------------------------------------------------------------------------------------

class Client(models.Model):
    business                = models.CharField(max_length=500, blank=True, null=True)
    first                   = models.CharField(max_length=500, blank=True, null=True)
    last                    = models.CharField(max_length=500, blank=True, null=True)
    street                  = models.CharField(max_length=500, blank=True, null=True)
    address2                = models.CharField(max_length=500, blank=True, null=True)
    email                   = models.EmailField(max_length=254)
    phone                   = models.CharField(max_length=500, blank=True, null=True)
    
    def __str__(self):
        return self.business
    
    
# -------------------------------------------------------------------------------------------


class Service(models.Model):
    service         = models.CharField(max_length=500, blank=True, null=True) 
    
    def __str__(self):
        return self.service
    

# -------------------------------------------------------------------------------------------

class Transaction(models.Model):
    date           = models.DateField(auto_now=False, auto_now_add=False)
    trans_type     = models.ForeignKey(Type, on_delete=models.PROTECT)
    category       = models.ForeignKey(Category, on_delete=models.PROTECT)
    sub_cat        = models.ForeignKey(SubCategory, on_delete=models.PROTECT)
    date_created   = models.DateField(auto_now_add=True)
    amount         = models.DecimalField(max_digits=20, decimal_places=2, blank=False)
    invoice_numb   = models.CharField(max_length=500, blank=True, null=True)
    paid           = models.CharField(max_length=500, blank=True, null=True, default="No")
    team           = models.ForeignKey('Team', null=True, on_delete=models.PROTECT)
    transaction    = models.CharField(max_length=500, blank=True, null=True)
    tax            = models.CharField(max_length=500, blank=True, null=True, default="Yes")
    keyword        = models.ForeignKey(Keyword, on_delete=models.PROTECT, default=1)
    receipt        = models.FileField(upload_to='receipts/', blank=True, null=True)

    class Meta:
        verbose_name_plural = "Transactions"
        ordering = ['date']

    def __str__(self):
        return self.transaction

    

    
# -------------------------------------------------------------------------------------------
    

class Invoice(models.Model):
    invoice_numb = models.CharField(max_length=10, unique=True)
    client = models.ForeignKey(Client, on_delete=models.PROTECT)
    event = models.CharField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=500, blank=True, null=True)
    keyword = models.ForeignKey(Keyword, on_delete=models.PROTECT, default=1)
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    amount = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
    date = models.DateField()
    due = models.DateField()
    paid = models.CharField(max_length=100, blank=True, null=True, default="No")

    class Meta:
        ordering = ['invoice_numb']

    def __str__(self):
        return self.invoice_numb

    def calculate_total(self):
        return sum(item.total for item in self.items.all())

# -------------------------------------------------------------------------------------------


class InvoiceItem(models.Model):
    invoice = models.ForeignKey('Invoice', on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Service, on_delete=models.PROTECT)
    qty = models.IntegerField(default=0)
    price = models.DecimalField(max_digits=20, decimal_places=2, default=0.00)

    def __str__(self):
        return f"{self.item.service} - {self.qty} x {self.price}"

    @property
    def total(self):
        return (self.qty or 0) * (self.price or 0)




 # -------------------------------------------------------------------------------------------
 

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

    date             = models.DateField()
    begin            = models.DecimalField(max_digits=10, decimal_places=1, null=True, validators=[MinValueValidator(0)])
    end              = models.DecimalField(max_digits=10, decimal_places=1, null=True, validators=[MinValueValidator(0)])
    total            = models.DecimalField(max_digits=10, decimal_places=1, null=True, editable=False)
    client           = models.ForeignKey('Client', on_delete=models.PROTECT)
    invoice          = models.CharField(max_length=255, blank=True, null=True)
    tax              = models.CharField(max_length=10, blank=False, null=True, default="Yes")
    job              = models.CharField(max_length=255, blank=True, null=True)
    vehicle          = models.CharField(max_length=255, blank=False, null=True, default="Lead Foot")

    mileage_type = models.CharField(max_length=20, choices=MILEAGE_TYPE_CHOICES, default='Taxable')

    class Meta:
        verbose_name_plural = "Miles"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.client}"

    def save(self, *args, **kwargs):
        # Automatically calculate total mileage
        if self.begin is not None and self.end is not None:
            self.total = round(self.end - self.begin, 1)
        else:
            self.total = None
        super().save(*args, **kwargs)




