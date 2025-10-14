from django import forms

class DealForm(forms.Form):
    TITLE = forms.CharField(label='Название сделки', max_length=255)
    TYPE_ID = forms.ChoiceField(label='Тип', choices=[])
    STAGE_ID = forms.ChoiceField(label='Стадия сделки', choices=[])
    OPPORTUNITY = forms.DecimalField(label='Сумма')
    CURRENCY_ID = forms.ChoiceField(label='Валюта', choices=[])
    BEGINDATE = forms.DateTimeField(
        label='Дата начала',
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    CLOSEDATE = forms.DateTimeField(
        label='Дата завершения',
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )
    UF_CRM_PRIORITY = forms.ChoiceField(label='Приоритет', choices=[])

    def clean(self):
        cleaned_data = super().clean()
        begindate = cleaned_data.get('BEGINDATE')
        closedate = cleaned_data.get('CLOSEDATE')

        if begindate and closedate and begindate > closedate:
            raise forms.ValidationError(
                "Дата начала сделки не может быть позже даты завершения"
            )

        return cleaned_data