from django.db import models
from django.contrib.auth.models import User
from game.models import Treasure

class GameConfiguration(models.Model):
    """Global game settings that admins can configure"""
    game_name = models.CharField(max_length=100, default="AR Treasure Hunt")
    is_game_active = models.BooleanField(default=True)
    max_players_per_session = models.IntegerField(default=100)
    default_treasure_points = models.IntegerField(default=100)
    default_discovery_radius = models.FloatField(default=50.0)
    leaderboard_refresh_interval = models.IntegerField(default=30)  # seconds
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Game Configuration"
        verbose_name_plural = "Game Configurations"
    
    def __str__(self):
        return f"{self.game_name} - {'Active' if self.is_game_active else 'Inactive'}"

class AdminAction(models.Model):
    """Log of admin actions for audit trail"""
    ACTION_CHOICES = [
        ('CREATE_TREASURE', 'Created Treasure'),
        ('EDIT_TREASURE', 'Edited Treasure'),
        ('DELETE_TREASURE', 'Deleted Treasure'),
        ('ACTIVATE_TREASURE', 'Activated Treasure'),
        ('DEACTIVATE_TREASURE', 'Deactivated Treasure'),
        ('CHANGE_SETTINGS', 'Changed Game Settings'),
        ('RESET_LEADERBOARD', 'Reset Leaderboard'),
    ]
    
    admin_user = models.ForeignKey(User, on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_treasure = models.ForeignKey(Treasure, on_delete=models.SET_NULL, null=True, blank=True)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Admin Action"
        verbose_name_plural = "Admin Actions"
    
    def __str__(self):
        return f"{self.admin_user.username} - {self.get_action_display()} at {self.timestamp}"

class TreasureTemplate(models.Model):
    """Pre-defined treasure templates that admins can quickly use"""
    name = models.CharField(max_length=100)
    description = models.TextField()
    points = models.IntegerField()
    discovery_radius = models.FloatField()
    category = models.CharField(max_length=50, default="General")
    difficulty_level = models.CharField(
        max_length=10,
        choices=[
            ('EASY', 'Easy'),
            ('MEDIUM', 'Medium'),
            ('HARD', 'Hard'),
            ('EXPERT', 'Expert')
        ],
        default='MEDIUM'
    )
    is_active_template = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'name']
        verbose_name = "Treasure Template"
        verbose_name_plural = "Treasure Templates"
    
    def __str__(self):
        return f"{self.name} ({self.category}) - {self.points} pts"