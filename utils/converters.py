from core.models import Book


def random_chars(n):
    """
    Returns a random character.
    """
    import random
    import string
    return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))


def convrt_book_slug_to_random_slug():
    """
    Converts a book slug to a random slug.
    """
    for book in Book.objects.all():
        slug = random_chars(6)
        while Book.objects.filter(slug=slug).exists():
            slug = random_chars(6)
        book.slug = slug
        book.save()

if __name__ == '__main__':
    convrt_book_slug_to_random_slug()