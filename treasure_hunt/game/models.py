from django.db import models
from django.contrib.auth.models import User


# Create your models here.

class Player(models.Model):
  user = models.OneToOneField(User, on_delete=models.CASCADE)
  total_score = models.IntegerField(default=0)
  treasures_found = models.IntegerField(default=0)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.user.username} - {self.total_score} points"

class Treasure(models.Model):
  name = models.CharField(max_length=100)
  description = models.TextField()
  latitude = models.FloatField()
  longitude = models.FloatField()
  points = models.IntegerField(default=100)
  is_active = models.BooleanField(default=True)
  discovery_radius = models.FloatField(default=50.0)
  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"{self.name} ({self.points} points)"


class Discovery(models.Model):
  player = models.ForeignKey(Player, on_delete=models.CASCADE)
  treasure = models.ForeignKey(Treasure, on_delete=models.CASCADE)
  discovered_at = models.DateTimeField(auto_now_add=True)
  player_latitude = models.FloatField()
  player_longitude = models.FloatField()

  class Meta:
    unique_together = ['player', 'treasure']

  def __str__(self):
    return f"{self.player.user.username} found {self.treasure.name}"