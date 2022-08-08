from django.contrib import admin
from .models import point_name, CustomUser



class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "username")
    list_display_links = ("id", "username")


admin.site.register(point_name)
admin.site.register(CustomUser, CustomUserAdmin)