from django.core.management.base import BaseCommand, CommandError

from utils.converters import convrt_book_slug_to_random_slug


class Command(BaseCommand):
    help = 'Convert book slugs to random slugs'

    def handle(self, *args, **options):
        convrt_book_slug_to_random_slug()
