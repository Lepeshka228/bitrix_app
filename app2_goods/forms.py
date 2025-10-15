from django import forms

class GoodForm(forms.Form):
    good_name = forms.CharField(label='Название товара',
                                widget=forms.TextInput(attrs={
                                    'id': 'good-input',
                                    'autocomplete': 'off',
                                    'placeholder': 'Введите название товара...'
                                }))
    good_id = forms.CharField(widget=forms.HiddenInput())
