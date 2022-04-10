from django.contrib import admin

from .models import Coordinates


@admin.register(Coordinates)
class CoordinatesAdmin(admin.ModelAdmin):
    pass
