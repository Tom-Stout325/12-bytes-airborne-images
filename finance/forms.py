from django import forms
from django.forms import inlineformset_factory
from .models import *



class TransForm(forms.ModelForm):
    keyword = forms.ModelChoiceField(
        queryset=Keyword.objects.all(),
        label='Keyword',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Transaction
        fields = (
            'date', 'trans_type', 'category', 'sub_cat', 'amount', 'invoice_numb',
            'keyword', 'paid', 'team', 'transaction', 'receipt'
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        if receipt:
            content_type = receipt.content_type
            if content_type not in ['application/pdf', 'image/jpeg', 'image/png']:
                raise forms.ValidationError("Only PDF, JPG, or PNG files are allowed.")
        return receipt


class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = ['invoice_numb', 'client', 'event', 'location', 'keyword', 'service', 'date', 'due', 'paid']


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['item', 'qty', 'price']


InvoiceItemFormSet = inlineformset_factory(
    Invoice,
    InvoiceItem,
    form=InvoiceItemForm,
    extra=5,
    can_delete=True
)


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['category']


class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['sub_cat']


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['business', 'first', 'last', 'street', 'address2', 'email', 'phone']
        
        
class MileageForm(forms.ModelForm):
    class Meta:
        model = Miles
        fields = ['date', 'begin', 'end', 'client', 'invoice', 'tax', 'job', 'vehicle', 'mileage_type']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'begin': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'end': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'invoice': forms.TextInput(attrs={'class': 'form-control'}),
            'tax': forms.TextInput(attrs={'class': 'form-control'}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle': forms.TextInput(attrs={'class': 'form-control'}),
            'mileage_type': forms.Select(attrs={'class': 'form-control'}),
        }      


class MileageRateForm(forms.ModelForm):
    class Meta:
        model = MileageRate
        fields = ['rate']



