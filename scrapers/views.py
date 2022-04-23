from core.models import Book
from . import thbook
from . import tasks

from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    if request.user.is_superuser:
        from_30book = Book.objects.filter(source="30book")
        recent_added_books = from_30book.order_by('-date_created')[:5]
        return HttpResponse("""
            <h1>Scrapers</h1>
            <p>Scrapers are used to get data from the web.</p>
            <p>This is the index page of the scrapers app.</p>
            <div>
                <a href="/scrapers/runfunction/">Run Function</a>
            </div>
            <div>
                <h4>
                    Book added to database from 30book:
                </h4>
                <p>
                    {0}
                </p>
                <p>
                    Recent added books:
                </p>
                <ul>
                    {1}
                </ul>
            </div>
            """.format(
                from_30book.count(),
                ''.join(['<li>{0}</li>'.format(book.title) for book in recent_added_books])
            )
        )


def runfunction(request):
    if request.user.is_superuser:
        tasks.add.delay(1, 2)
        # thbook.main()
        return HttpResponse("Fetching data from the web...")
