from django import forms
from pandas import read_excel
from .models import Contact
class ContactAdminForm(forms.ModelForm):
    excel_file = forms.FileField(required=False, label='فایل اکسل')

    class Meta:
        model = Contact
        fields =['excel_file']


    def clean_excel_file(self):
        excel_file = self.cleaned_data.get('excel_file')
        if not excel_file:
            return None
        if not excel_file.name.endswith('.xlsx'):
            raise forms.ValidationError('فقط فرمت xlsx مجاز است')
        df = read_excel(excel_file,dtype=str)
        return df

