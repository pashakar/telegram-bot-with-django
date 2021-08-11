from django.contrib import admin
from .models import DataUser


@admin.register(DataUser)
class DataUserAdmin(admin.ModelAdmin):
    pass

