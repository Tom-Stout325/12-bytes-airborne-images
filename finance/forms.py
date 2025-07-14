from django import forms
from django.forms import inlineformset_factory
from .models import *



class TransForm(forms.ModelForm):
    keyword = forms.ModelChoiceField(
        queryset=Keyword.objects.order_by('name'),
        label='Keyword',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    sub_cat = forms.ModelChoiceField(
        queryset=SubCategory.objects.all().order_by('category__category', 'sub_cat'),
        label='Sub-Category',
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = Transaction
        fields = (
            'date', 'trans_type', 'sub_cat', 'amount',
            'invoice_numb', 'team','transaction', 'receipt',
            'transport_type', 'keyword'
        )
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'transport_type': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean_receipt(self):
        receipt = self.cleaned_data.get('receipt')
        if receipt and hasattr(receipt, 'content_type'):
            if receipt.content_type not in ['application/pdf', 'image/jpeg', 'image/png']:
                raise forms.ValidationError("Only PDF, JPG, or PNG files are allowed.")
        return receipt

    def clean(self):
        cleaned_data = super().clean()
        transport = cleaned_data.get("transport_type")
        sub_cat = cleaned_data.get("sub_cat")

        if sub_cat:
            cleaned_data['category'] = sub_cat.category

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if instance.sub_cat:
            instance.category = instance.sub_cat.category
        if commit:
            instance.save()
        return instance





class InvoiceForm(forms.ModelForm):
    class Meta:
        model = Invoice
        exclude = ['amount']  # keep amount excluded, it's calculated
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'due': forms.DateInput(attrs={'type': 'date'}),
            'paid_date': forms.DateInput(attrs={'type': 'date'}),
            'keyword': forms.Select(attrs={'class': 'form-select'}), 
        }


class InvoiceItemForm(forms.ModelForm):
    class Meta:
        model = InvoiceItem
        fields = ['description', 'qty', 'price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control'}),
            'qty': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }



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
        widgets = {
            'category': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter category name'
            }),
        }




class SubCategoryForm(forms.ModelForm):
    class Meta:
        model = SubCategory
        fields = ['sub_cat', 'category'] 
        widgets = {
            'sub_cat': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter sub-category name'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }



class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['business', 'first', 'last', 'street', 'address2', 'email', 'phone']




class MileageForm(forms.ModelForm):
    class Meta:
        model = Miles
        exclude = ['user', 'total']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'begin': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'end': forms.NumberInput(attrs={'step': '0.1', 'class': 'form-control'}),
            'client': forms.Select(attrs={'class': 'form-control'}),
            'invoice': forms.Select(attrs={'class': 'form-control'}),  # changed from TextInput to Select
            'tax': forms.TextInput(attrs={'class': 'form-control'}),
            'job': forms.TextInput(attrs={'class': 'form-control'}),
            'vehicle': forms.TextInput(attrs={'class': 'form-control'}),
            'mileage_type': forms.Select(attrs={'class': 'form-control'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['invoice'].queryset = Invoice.objects.order_by('-date')



class MileageRateForm(forms.ModelForm):
    class Meta:
        model = MileageRate
        fields = ['rate']
        widgets = {
            'rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }

class KeywordForm(forms.ModelForm):
    class Meta:
        model = Keyword
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class RecurringTransactionForm(forms.ModelForm):
    class Meta:
        model = RecurringTransaction
        fields = [
            'user', 'trans_type', 'category', 'sub_cat', 'amount', 'transaction', 'day',
            'team', 'keyword', 'tax', 'receipt', 'active'
        ]
        widgets = {
            'day': forms.NumberInput(attrs={'min': 1, 'max': 28}),
        }
