from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # API endpoints
    path('api/nearby-treasures/', views.get_nearby_treasures, name='nearby_treasures'),
    path('api/discover-treasure/', views.discover_treasure, name='discover_treasure'),
    path('api/leaderboard/', views.leaderboard, name='leaderboard'),
    path('api/treasures/', views.get_all_treasures, name='all_treasures'),
    path('api/admin/create-treasure/', views.create_treasure, name='create_treasure'),
    
    # Frontend pages
    path('', TemplateView.as_view(template_name='game/index.html'), name='home'),
    path('play/', TemplateView.as_view(template_name='game/ar-view.html'), name='ar_game'),
    path('leaderboard/', TemplateView.as_view(template_name='game/leaderboard.html'), name='leaderboard_page'),
]