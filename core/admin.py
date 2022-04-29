from django.contrib import admin
from core.models import *


admin.site.register(CategoryPosts)
admin.site.register(UserProfile)
admin.site.register(Author)
admin.site.register(BookList)
admin.site.register(Publisher)
admin.site.register(Translator)
admin.site.register(Review)
@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'publisher', 'cover_type', 'size')
    list_filter = ('publisher', 'cover_type', 'size', 'authors__name', 'translators__name')
    search_fields = ('title', 'publisher', 'cover_type', 'size', 'authors__name', 'translators__name')
    readonly_fields = ('user_liked', 'user_readers', 'reviews', 'raw_data', 'slug', 'date_created',)
admin.site.register(Size)
admin.site.register(CoverType)
admin.site.register(About)
admin.site.register(Report)
admin.site.register(ReportBook)
admin.site.register(Baners)
