import pandas as pd
from django.shortcuts import render
from django.http import HttpResponse

from web.forms import UploadFileForm
from core.models import Translator, Author, Book, CoverType, Size, Publisher

def upload_file(request):
    # only authenticated staff users can upload files
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to upload files")

    elif request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            file = request.FILES['file']
            df = pd.read_excel(file)
            data = df.to_dict(orient='records')
            for row in data:
                name = row.get('Book')
                if name != None and name != '' and type(name) == str:
                    name = name.strip()
                    if Book.objects.filter(title=name).exists():
                        continue
                    else:
                        book = Book.objects.create(title=name)

                author = row.get('Author-Farsi')
                if author != None and author != '' and type(author) == str:
                    author = author.strip()
                    author = Author.objects.get_or_create(name=author)[0]
                    book.authors.add(author)

                translator = row.get('Translator')
                if translator != None and translator != '' and type(translator) == str:
                    translator = translator.strip()
                    translator = Translator.objects.get_or_create(name=translator)[0]
                    book.translators.add(translator)

                shabak = row.get('Shabak')
                if shabak != None and shabak != '' and type(shabak) == str:
                    shabak = shabak.strip()
                    book.isbn = shabak

                qte = row.get('QTE')
                if qte != None and qte != '' and type(qte) == str:
                    qte = qte.strip()
                    qte = Size.objects.get_or_create(name=qte)[0]
                    book.size = qte

                pages = row.get('Pages')
                if pages != None and pages != '' and type(pages) == int or type(pages) == str:
                    book.pages = pages

                jeld = row.get('Jeld')
                if jeld != None and jeld != '' and type(jeld) == str:
                    jeld = jeld.strip()
                    jeld = CoverType.objects.get_or_create(name=jeld)[0]
                    book.cover_type = jeld

                publisher = Publisher.objects.get(name=form.cleaned_data['publisher'])
                book.publisher = publisher                
                book.cover = ''

                book.save()

            return HttpResponse('OK')
    else:
        form = UploadFileForm()
    return render(request, 'web/upload_file.html', {'form': form})


def choose_photos(request):
    if not request.user.is_staff:
        return HttpResponse("You are not authorized to upload files")

    data = Book.objects.filter(cover='')
    return render(request, 'web/choose_photos.html', {'books': data})
