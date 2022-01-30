import os
import pandas as pd

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse

from web.forms import *
from web.functions import translator
from core.models import BookRawData, Translator, Author, Book, CoverType, Size, Publisher


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


def index(request):
    if not request.user.is_staff:
        return redirect(reverse('admin:login'))
    count = BookRawData.objects.filter(is_active=True).count()
    return render(request, 'web/index.html', {'count': count})


def create_book_obj_view(request, number=0):
    if not request.user.is_staff:
        return redirect(reverse('admin:login'))

    if request.method == 'GET':
        form_book = BookForm()
        raw_books = BookRawData.objects.filter(is_active=True)
        if number:
            raw_book = raw_books[int(number)]
        data = {}

        data['raw_book'] = raw_book.data.get('RAW', '')
        try:
            data['isbn']= int(raw_book.data.get('ISBN', '')[0].strip())
        except IndexError:
            data['isbn'] = ''
        except:
            data['isbn'] = ''
        try:
            data['title']= raw_book.data.get('onvan-padid_avarandeh', '')[0].strip()
        except:
            data['title'] = ''
        
        data['subtitle']= ''
        
        try:
            data['author']= raw_book.data.get('author', '')[0].strip()
        except:
            data['author'] = ''
        try:
            data['translator']= raw_book.data.get('translator', '')[0].strip()
        except:
            data['translator'] = ''
        data['publisher']= ''
        data['pages']= raw_book.data.get('moshakhasat-zaheri', '')
        try:
            data['pages'] = int(data['pages'][0].strip())
        except:
            data['pages'] = 0
        try:
            data['language']= raw_book.data.get('zaban', '')[0].strip()
        except:
            data['language'] = ''
        data['org'] = raw_book.data

        context = {
            'form_book': form_book,
            'raw_book': raw_book.data,
            'data': data,
            'next': int(number) + 1,
            'prev': int(number) - 1,
        }
        return render(request, 'web/create_book_obj.html', context)

    elif request.method == 'POST':
        form_book = BookForm(request.POST)
        if form_book.is_valid():
            raw_book = BookRawData.objects.filter(is_active=True)[int(number)-1]
            label = ', '.join(raw_book.data['mozo'])
            book = Book.objects.create(
                raw_data=raw_book.data,
                label=label.strip(),
                title=form_book.cleaned_data['title'],
                subtitle=form_book.cleaned_data['subtitle'],
                publisher=form_book.cleaned_data['publisher'],
                pages=form_book.cleaned_data['pages'],
                language=form_book.cleaned_data['language'],
                size=form_book.cleaned_data['size'],
                cover_type=form_book.cleaned_data['cover_type'],
            )
            book.authors.add(form_book.cleaned_data['author'])
            book.translators.add(form_book.cleaned_data['translator'])
            book.save()
            raw_book.is_active = False
            raw_book.save()
            return redirect(reverse('web:create_book_obj_view', args=[int(number)]))
        else:
            return render(request, 'web/create_book_obj.html', {'form_book': form_book, 'next': int(number) + 1, 'prev': int(number) - 1})
    # return render(request, 'create_book_obj.html', {'raw_book': raw_book})
