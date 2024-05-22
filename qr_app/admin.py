from django.contrib import admin
from .models import Postcard, MediaFile

admin.site.register(Postcard)

@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('postcard', 'file')