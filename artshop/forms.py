from django import forms
from .models import Size, Frame, Material

class CustomerForm(forms.Form):
    first_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    phone = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    postal_code = forms.CharField(max_length=20, widget=forms.TextInput(attrs={'class': 'form-control'}))
    special_instructions = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))

class ArtworkCustomizationForm(forms.Form):
    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    frame = forms.ModelChoiceField(
        queryset=Frame.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    material = forms.ModelChoiceField(
        queryset=Material.objects.all(),
        empty_label=None,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
