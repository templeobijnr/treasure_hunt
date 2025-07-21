from django.contrib import admin
from .models import GameConfiguration, AdminAction, TreasureTemplate

@admin.register(GameConfiguration)
class GameConfigurationAdmin(admin.ModelAdmin):
    list_display = ['game_name', 'is_game_active', 'max_players_per_session', 'default_treasure_points', 'updated_at']
    list_editable = ['is_game_active', 'max_players_per_session', 'default_treasure_points']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(AdminAction)
class AdminActionAdmin(admin.ModelAdmin):
    list_display = ['admin_user', 'action', 'target_treasure', 'timestamp', 'ip_address']
    list_filter = ['action', 'timestamp']
    search_fields = ['admin_user__username', 'description']
    readonly_fields = ['timestamp']

@admin.register(TreasureTemplate)
class TreasureTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'difficulty_level', 'points', 'discovery_radius', 'is_active_template']
    list_filter = ['category', 'difficulty_level', 'is_active_template']
    search_fields = ['name', 'description']
    list_editable = ['is_active_template']
    readonly_fields = ['created_at']