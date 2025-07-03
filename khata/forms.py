from django import forms
from .models import Item, Invoice

class ItemForm(forms.ModelForm):
    class Meta:
        model = Item
        fields = ['name', 'description', 'price', 'quantity']

class InvoiceForm(forms.ModelForm):
    tax_type = forms.ChoiceField(choices=[('percent', '%'), ('fixed', 'Fixed')], required=False)
    tax_value = forms.DecimalField(required=False, initial=0)
    discount_type = forms.ChoiceField(choices=[('percent', '%'), ('fixed', 'Fixed')], required=False)
    discount_value = forms.DecimalField(required=False, initial=0)
    customer_name = forms.CharField(required=False)
    customer_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number'
        })
    )
    customer_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Address'
        })
    )

    class Meta:
        model = Invoice
        fields = ['customer_name']

class AddItemForm(forms.Form):
    item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1)

