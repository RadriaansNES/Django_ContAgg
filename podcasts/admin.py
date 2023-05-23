from django.contrib import admin
from .models import Episode

## tell django admin to display episode data
@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ("podcast_name", "title", "pub_date")