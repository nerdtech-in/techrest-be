from django import forms
from .models import Menu
class OrderForm(forms.Form):
    item = forms.ModelChoiceField(queryset=Menu.objects.all(), empty_label=None)
    quantity = forms.IntegerField(min_value=1)