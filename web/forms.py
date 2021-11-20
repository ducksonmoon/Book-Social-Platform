from django import forms

from core.models import Publisher


class UploadFileForm(forms.Form):
    file = forms.FileField()
    publisher = forms.ModelChoiceField(queryset=Publisher.objects.all(), empty_label="Select a publisher")
    
    def clean_file(self):
        # Check file is .xlsx or .xls 
        file = self.cleaned_data['file']
        if not file.name.endswith('.xlsx') and not file.name.endswith('.xls'):
            raise forms.ValidationError('File is not .xlsx or .xls')
        return file

    def save(self):
        file = self.cleaned_data['file']
        return file