from django.contrib import admin
from core.models import *

admin.site.register(User)
admin.site.register(UserProfile)
admin.site.register(Book)
admin.site.register(Author)
admin.site.register(Publisher)
admin.site.register(Translator)
admin.site.register(Review)