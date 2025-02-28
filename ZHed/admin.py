from django.contrib import admin # Importing Admin Module To Manage Models In The Admin Interface
from .models import Word, Player # Importing Models To Manage In The Admin Panel

# Word Model Registration & Admin Panel Appearance Customization
@admin.register(Word)
class WordAdmin(admin.ModelAdmin):
    list_display = ("word", "hint", "meaning", "translation","translated_definition") # Specifies Columns To Display in The Admin List View
    search_fields = ("word", "meaning", "translation") # Allows Search By These Fields In The Admin Interface
    ordering = ['created_at']  # Order words by created_at field in ascending order (oldest first)

# Player Model Registration & Admin Panel Appearance Customization
@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ("name", "score", "level", "correct_guesses_count") # Specifies Columns To Display in The Admin List View
    search_fields = ("name",) # Allows Search By These Fiels In The Admin Interface

