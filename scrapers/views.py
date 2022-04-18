from . import thbook

from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    if request.user.is_superuser:
        return HttpResponse("""
            <h1>Scrapers</h1>
            <p>Scrapers are used to get data from the web.</p>
            <p>This is the index page of the scrapers app.</p>
            <div>
                <a href="/scrapers/thbook/">ThBook</a>
            </div>
            <div>
                <h6> Count: %s </h6>
            </div>
            """)


def thbook(request):
    if request.user.is_superuser:
        thbook.main()
        return HttpResponse("Fetching data from the web...")
