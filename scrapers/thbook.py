import json, re
import time, sys, os
import requests
from io import BytesIO

from django.core.files import File
from django.core.files.temp import NamedTemporaryFile

from requests import get
from requests.exceptions import RequestException
from contextlib import closing
from bs4 import BeautifulSoup

from farsi_tools import standardize_persian_text
import pyarabic.araby as araby

from core.models import Book, Author, Translator, Size, CoverType, Publisher


def html2text(html):
    """
    Convert HTML to text
    """
    soup = BeautifulSoup(html, 'html.parser')
    return soup.get_text()


def is_good_response(resp):
    """
    Returns True if the response seems to be HTML, False otherwise.
    """
    content_type = resp.headers['Content-Type'].lower()
    return (resp.status_code == 200
            and content_type is not None
            and content_type.find('html') > -1)

def log_error(e):
    print(e)

def log_actions(action):
    print(action)
    dir = os.path.dirname(os.path.abspath(__file__))
    log = open(dir + "/temp/requests.log", "a")
    log.write(
        "{}: - {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), action)
        )
    log.close()

def simple_get(url):
    """
    Attempts to get the content at `url` by making an HTTP GET request.
    If the content-type of response is some kind of HTML/XML, return the
    text content, otherwise return None.
    """
    try:
        with closing(get(url, stream=True)) as resp:
            if is_good_response(resp):
                return resp.content
            else:
                return None
    except RequestException as e:
        log_error('Error during requests to {0} : {1}'.format(url, str(e)))
        return None


class Crawl:

    def get_next_page_url(self, page_number):
        base_url = 'https://nashremahi.com/shop/page/{}/'.format(page_number)
        return base_url

    def log_error(self, e):
        print(e)

    def log_actions(self, action):
        print(action)
        dir = os.path.dirname(os.path.abspath(__file__))

        log = open(dir+"/temp/requests.log", "a")
        log.write(
            "{}: - {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"), action)
            )
        log.close()

    def is_good_response(self, resp):
        """
        Returns True if the response seems to be HTML, False otherwise.
        """
        content_type = resp.headers['Content-Type'].lower()
        return (resp.status_code == 200
                and content_type is not None
                and content_type.find('html') > -1)

    def simple_get(self, url):
        """
        Attempts to get the content at `url` by making an HTTP GET request.
        If the content-type of response is some kind of HTML/XML, return the
        text content, otherwise return None.
        """
        try:
            with closing(get(url, stream=True)) as resp:
                if self.is_good_response(resp):
                    return resp.content
                else:
                    return None

        except RequestException as e:
            self.log_error('Error during requests to {0} : {1}'.format(url, str(e)))
            return None

    def get_page_string_data(self, url):
        """
        Get the data of the page
        """
        content = self.simple_get(url)
        # Convert the bytes response to a string
        content = content.decode('utf-8')
        return content

    def extract_book_urls(self, url, function_name):
        """
        Extract the book urls from the page
        """
        content = self.get_page_string_data(url)
        book_urls = function_name(content)
        return book_urls




def prosessPage_30book(url):
    resp = simple_get(url)
    if resp is not None:
        text = html2text(resp)
    else:
        log_actions(
            "No response for url: {}".format(url)
        )
        return None
    # Remove all 2 or more new lines
    text = re.sub(r'\n{2,}', '\n', text)
    # Remove all spaaces more than one
    text = re.sub(r'\s{2,}', '\n', text)
    # Split by نظرات کاربران
    text = text.split('نظرات کاربران')[0]


    # author: If starts with نویسنده:
    # There is only one author
    if "نویسنده:" in text:
        author = re.findall(r'نویسنده:[^\n]+', text)
        if len(author) == 0:
            author = None
        else:
            author = author[0].replace("نویسنده:", "").strip()
    elif "نویسندگان:" in text:
        author = re.findall(r'نویسندگان:[^\n]+', text)
        if len(author) == 0:
            author = None
        else:
            author = author[0].replace("نویسندگان:", "").strip()
        temps = re.findall(r'{0}[^\n]+'.format(author.split()[0]), text)
        # if any contains ، select and split it
        if len(author) == 0:
            author = None
        else:
            for i in temps:
                if "،" in i:
                    author = i.split("،")
                    break
    else:
        author = None


    # title: It starts with خرید کتاب and ends with اثر
    title = re.findall(r'خرید کتاب[^\n]+اثر', text)
    if len(title) == 0:
        title = None
    else:
        title = title[0].replace("خرید کتاب", "").replace("اثر", "")
    # Translator: If starts with مترجم:
    """
    translator = re.findall(r'مترجم:[^\n]+', text)
    if "مترجم:" not in text:
        translator = None
    elif len(translator) == 0:
        translator = None
    else:
        translator = translator[0].replace("مترجم:", "").strip()
    """
    if "مترجم:" in text:
        translator = re.findall(r'مترجم:[^\n]+', text)
        if len(translator) == 0:
            translator = None
        else:
            translator = translator[0].replace("مترجم:", "").strip()
    elif "مترجمان:" in text:
        translator = re.findall(r'مترجمان:[^\n]+', text)
        if len(translator) == 0:
            translator = None
        else:
            translator = translator[0].replace("مترجمان:", "").strip()
        temps = re.findall(r'{0}[^\n]+'.format(translator.split()[0]), text)
        # if any contains ، select and split it
        if len(translator) == 0:
            translator = None
        else:
            for i in temps:
                if "،" in i:
                    translator = i.split("،")
                    break
    else:
        translator = None
    # ISBN: find number between 10 and 13 digits
    isbn = re.findall(r'\d{10,13}', text)
    if len(isbn) == 0:
        isbn = None
    else:
        isbn = isbn[0]
    # Publisher: Is starts with نشر: and new line after it
    publisher = re.findall(r'نشر:\n[^\n]+', text)
    if len(publisher) == 0:
        publisher = None
    else:
        publisher = publisher[0].replace("نشر:", "").replace("\n", "")
    
    coverTypes = [
        "شومیز", "کاغذی", "گالینگور", "سخت",
    ]
    # If any of the coverTypes in the text assign it to coverType
    coverType = None
    if "جلد کتاب" in text:
        for c in coverTypes:
            cover = re.findall(r'{0}\n'.format(c), text)
            if len(cover) > 0:
                coverType = c
                break

    sizeTypes = [
        "رحلی بزرگ", "رحلی کوچک", "خشتی", 
        "۲۴×۱۶/۸", "رقعی", "جیبی", "پالتویی",
        "وزیری", "رحلی", "سلطانی", "جیبی بزرگ",
        "خشتی کوچک", "خشتی بزرگ", "جیبی کوچک", 
    ]
    # If any of the sizeTypes in the text assign it to sizeType
    sizeType = None
    if "قطع کتاب" in text:
        for s in sizeTypes:
            size = re.findall(r'{0}\n'.format(s), text)
            if len(size) > 0:
                sizeType = s
                break

    # Pages Count: is numbers before صفحه
    pagesCount = re.findall(r'\d+ صفحه', text)
    if len(pagesCount) == 0:
        pagesCount = None
    else:
        pagesCount = pagesCount[0].replace("صفحه", "")
    # Code after book/ in url
    code = re.findall(r'book/[^/]+/', url)
    code = code[0].replace("book/", "").replace("/", "")
    coverUrl = f"https://www.30book.com/Media/Book/{code}.jpg"
    info = {
        "title": title.strip(),
        "author": author,
        "translator": translator,
        "isbn": isbn.strip(),
        "publisher": publisher.strip(),
        "coverType": coverType,
        "sizeType": sizeType,
        "pagesCount": pagesCount.strip(),
        "url": url,
        "coverUrl": coverUrl,
    }
    # file_test = open("temp/test.txt", "w")
    # file_test.write(text)
    return info



crawl = Crawl()

def collect(url):
    if url != "":
        info = prosessPage_30book(url)
        if info != None:
            return info
        else:
            crawl.log_actions("No info for url: {}".format(url))


def clean_persian_chars(text):
    text = text.replace("‌", " ")
    text = standardize_persian_text(text)
    text = araby.strip_diacritics(text)
    return text


def main():
    dir = os.path.dirname(os.path.abspath(__file__))
    existed_publishers = [
        'بیدگل', 'کرگدن', 'پارسه', 'افق', 'تاش', 'اطراف',
        'آریاناقلم', 'آریانا قلم', 'دف', 'کارنامه', 'نی',
    ]
    urls = open(dir + "/book-urls.txt").read().split("\n")
    # book-urls
    for url in urls:
        r = collect(url)
        if r['publisher'] in existed_publishers:
            continue
        elif Book.objects.filter(isbn=r["isbn"].strip()).count() > 0:
            continue
        else:
            book = Book(
                title=r["title"],
                isbn=r["isbn"].strip(),
            )
            book.save()
            try:
                book.pages = int(r["pagesCount"])
            except:
                pass
 
            if r["translator"] == None:
                pass
            elif type(r["translator"]) == list:
                for t in r['translator']:
                    t = t.strip()
                    if Translator.objects.filter(name=t).count() > 0:
                        translator = Translator.objects.get(name=t)
                    else:
                        translator = Translator(
                            name=t,
                        )
                        translator.save()
                    book.translators.add(translator)
            else:
                if Translator.objects.filter(name=r["translator"]).count() > 0:
                    translator = Translator.objects.get(name=r["translator"])
                else:
                    translator = Translator(
                        name=r["translator"],
                    )
                    translator.save()
                book.translators.add(translator)

            if r["author"] == None:
                pass
            elif type(r["author"]) == list:
                for a in r['author']:
                    a = a.strip()
                    if Author.objects.filter(name=a).count() > 0:
                        author = Author.objects.get(name=a)
                    else:
                        author = Author(
                            name=a,
                        )
                        author.save()
                    book.authors.add(author)     
            else:
                if Author.objects.filter(name=r["author"]).count() > 0:
                    author = Author.objects.get(name=r["author"])
                else:
                    author = Author(
                        name=r["author"],
                    )
                    author.save()
                book.authors.add(author)

            if r["publisher"] != None:
                if Publisher.objects.filter(name=r["publisher"]).count() > 0:
                    book.publisher = Publisher.objects.get(name=r["publisher"])
                else:
                    publisher = Publisher(
                        name=r["publisher"],
                    )
                    publisher.save()
                    book.publisher = publisher

            
            if r["coverType"] == None:
                pass
            elif CoverType.objects.filter(name=r["coverType"]).count() > 0:
                book.cover_type = CoverType.objects.get(name=r["coverType"])
            else:
                cover_type = CoverType(
                    name=r["coverType"],
                )
                cover_type.save()
                book.cover_type = cover_type
            
            if r["sizeType"] == None:
                pass
            elif Size.objects.filter(name=r["sizeType"]).count() > 0:
                book.size = Size.objects.get(name=r["sizeType"])
            else:
                size = Size(
                    name=r["sizeType"],
                )
                size.save()
                book.size = size
        
            try:
                image = requests.get(r["coverUrl"], timeout=10)
                image.raise_for_status()
                image_file = BytesIO(image.content)
                book.cover.save(r["coverUrl"].split("/")[-1], File(image_file))
            except Exception as e:
                print(e)
                pass
            
            book.source = "30book"
            book.source_link = r["url"]
            book.save()
            crawl.log_actions("New book added: {}".format(r["title"]))
        """
        # add dict to book-info.json
        with open(dir + "/temp/book-info.json", "a") as f:
            f.write(json.dumps(r, ensure_ascii=False) + "," + "\n")
            f.flush()
        """