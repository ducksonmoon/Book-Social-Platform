from django import forms

from core.models import Author, CoverType, Size, Translator, Publisher


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


class BookForm(forms.Form):
    title = forms.CharField(max_length=225)
    subtitle = forms.CharField(max_length=225, required=False)
    author = forms.CharField(max_length=225, required=False)
    translator = forms.CharField(max_length=225, required=False)
    publisher = forms.CharField(max_length=225, required=False)
    pages = forms.IntegerField(required=False)
    isbn = forms.IntegerField(required=False)
    language = forms.CharField(max_length=225, required=False)
    size = forms.ModelChoiceField(queryset=Size.objects.all(), required=False)
    cover_type = forms.ModelChoiceField(queryset=CoverType.objects.all(), required=False)

    # Check if author is already in the database or not create new author
    def clean_author(self):
        author = self.cleaned_data['author']
        if Author.objects.filter(name=author).exists():
            return Author.objects.get(name=author)
        else:
            return Author.objects.create(name=author)

    # Check if translator is already in the database or not create new translator
    def clean_translator(self):
        translator = self.cleaned_data['translator']
        if Translator.objects.filter(name=translator).exists():
            return Translator.objects.get(name=translator)
        else:
            return Translator.objects.create(name=translator)
    
    # Check if publisher is already in the database or not create new publisher
    def clean_publisher(self):
        publisher = self.cleaned_data['publisher']
        if Publisher.objects.filter(name=publisher).exists():
            return Publisher.objects.get(name=publisher)
        else:
            return Publisher.objects.create(name=publisher)

    
    def clean_pages(self):
        pages = self.cleaned_data['pages']
        if pages is None:
            return 0
        else:
            return pages
