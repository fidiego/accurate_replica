from django.contrib import admin

from fax.models import Fax


class FaxModelAdmin(admin.ModelAdmin):
    list_display = ('sid', 'direction', '_to', '_from', 'created_on', 'created_by')
    ordering = ['-created_on']

admin.site.register(Fax, FaxModelAdmin)
