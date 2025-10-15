from django import forms

class GoodForm(forms.Form):
    good_name = forms.CharField(label='Название товара',
                                widget=forms.TextInput(attrs={
                                    'id': 'good_input',
                                    'autocomplete': 'off',
                                    'placeholder': 'Введите название товара...'
                                }))
