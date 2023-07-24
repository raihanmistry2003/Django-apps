from django.contrib import admin
from core.models import *

@admin.register(urls)
class UrlsAdmin(admin.ModelAdmin):
    list_display = ['short_url','long_url', 'url_hit_count']

@admin.register(User)
class userAdmin(admin.ModelAdmin):
    list_display = ['email', 'first_name','last_name', 'email_token', 'is_email_varified']

@admin.register(Qrcodes)
class qrcodesAdmin(admin.ModelAdmin):
    list_display = ['email', 'long_url','title', 'qrcode']
