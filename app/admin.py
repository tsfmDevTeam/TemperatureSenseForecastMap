from django.contrib import admin
from .models import point_name, CustomUser



class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("user_id", "username")
    list_display_links = ("user_id", "username")


admin.site.register(point_name)
admin.site.register(CustomUser, CustomUserAdmin)