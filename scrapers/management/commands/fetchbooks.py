from django.core.management.base import BaseCommand, CommandError
from scrapers import thbook


class Command(BaseCommand):
    help = 'Fetch data from the web'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Start fetching books...'))
        thbook.main()
        self.stdout.write(self.style.SUCCESS('Successfully fetched data from the web'))
