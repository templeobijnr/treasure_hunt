from django.contrib import admin
from .models import Player, Treasure, Discovery

@admin.register(Player)
class PlayerAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_score', 'treasures_found', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']

@admin.register(Treasure)
class TreasureAdmin(admin.ModelAdmin):
    list_display = ['name', 'points', 'latitude', 'longitude', 'is_active', 'discovery_radius', 'created_at']
    list_filter = ['is_active', 'created_at', 'points']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    list_editable = ['is_active', 'points']

@admin.register(Discovery)
class DiscoveryAdmin(admin.ModelAdmin):
    list_display = ['player', 'treasure', 'discovered_at', 'player_latitude', 'player_longitude']
    list_filter = ['discovered_at', 'treasure']
    search_fields = ['player__user__username', 'treasure__name']
    readonly_fields = ['discovered_at']