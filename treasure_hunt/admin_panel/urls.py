from django.urls import path
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    path('', staff_member_required(TemplateView.as_view(template_name='admin/dashboard.html')), name='admin_dashboard'),
    path('api/stats/', views.get_game_stats, name='game_stats'),
    path('api/templates/', views.get_treasure_templates, name='treasure_templates'),
    path('api/create-from-template/', views.create_treasure_from_template, name='create_from_template'),
    path('api/toggle-treasure/', views.toggle_treasure_status, name='toggle_treasure'),
    path('api/delete-treasure/<int:treasure_id>/', views.delete_treasure, name='delete_treasure'),
]