from django.contrib import admin
from core.models import *

admin.site.register(UserProfile)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Translator)
admin.site.register(Review)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # pre populating for Book.slug
    prepopulated_fields = {'slug': ('title',)}
