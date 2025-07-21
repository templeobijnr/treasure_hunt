from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from game.models import Treasure, Player, Discovery
from .models import GameConfiguration, AdminAction, TreasureTemplate
from django.contrib.auth.models import User
from django.utils import timezone
import json

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard view"""
    return render(request, 'admin/dashboard.html')

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_game_stats(request):
    """Get overall game statistics for admin dashboard"""
    total_players = Player.objects.count()
    total_treasures = Treasure.objects.count()
    active_treasures = Treasure.objects.filter(is_active=True).count()
    total_discoveries = Discovery.objects.count()
    
    # Recent activity (last 24 hours)
    from datetime import datetime, timedelta
    yesterday = timezone.now() - timedelta(days=1)
    recent_discoveries = Discovery.objects.filter(discovered_at__gte=yesterday).count()
    new_players = Player.objects.filter(created_at__gte=yesterday).count()
    
    return Response({
        'total_players': total_players,
        'total_treasures': total_treasures,
        'active_treasures': active_treasures,
        'total_discoveries': total_discoveries,
        'recent_discoveries': recent_discoveries,
        'new_players': new_players
    })

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_treasure_templates(request):
    """Get available treasure templates"""
    templates = TreasureTemplate.objects.filter(is_active_template=True)
    data = [{
        'id': t.id,
        'name': t.name,
        'description': t.description,
        'points': t.points,
        'discovery_radius': t.discovery_radius,
        'category': t.category,
        'difficulty_level': t.difficulty_level
    } for t in templates]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_treasure_from_template(request):
    """Create a treasure using a template"""
    try:
        template_id = request.data.get('template_id')
        latitude = float(request.data.get('latitude'))
        longitude = float(request.data.get('longitude'))
        
        template = TreasureTemplate.objects.get(id=template_id)
        
        treasure = Treasure.objects.create(
            name=template.name,
            description=template.description,
            latitude=latitude,
            longitude=longitude,
            points=template.points,
            discovery_radius=template.discovery_radius
        )
        
        # Log admin action
        AdminAction.objects.create(
            admin_user=request.user,
            action='CREATE_TREASURE',
            target_treasure=treasure,
            description=f"Created treasure '{treasure.name}' from template '{template.name}'",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'id': treasure.id,
            'message': f'Treasure created from template: {template.name}'
        })
        
    except TreasureTemplate.DoesNotExist:
        return Response({'error': 'Template not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def toggle_treasure_status(request):
    """Activate or deactivate a treasure"""
    try:
        treasure_id = request.data.get('treasure_id')
        treasure = Treasure.objects.get(id=treasure_id)
        
        treasure.is_active = not treasure.is_active
        treasure.save()
        
        action = 'ACTIVATE_TREASURE' if treasure.is_active else 'DEACTIVATE_TREASURE'
        AdminAction.objects.create(
            admin_user=request.user,
            action=action,
            target_treasure=treasure,
            description=f"{'Activated' if treasure.is_active else 'Deactivated'} treasure '{treasure.name}'",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        return Response({
            'message': f"Treasure {'activated' if treasure.is_active else 'deactivated'}",
            'is_active': treasure.is_active
        })
        
    except Treasure.DoesNotExist:
        return Response({'error': 'Treasure not found'}, status=404)

@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_treasure(request, treasure_id):
    """Delete a treasure"""
    try:
        treasure = Treasure.objects.get(id=treasure_id)
        treasure_name = treasure.name
        
        # Log before deleting
        AdminAction.objects.create(
            admin_user=request.user,
            action='DELETE_TREASURE',
            description=f"Deleted treasure '{treasure_name}'",
            ip_address=request.META.get('REMOTE_ADDR')
        )
        
        treasure.delete()
        
        return Response({'message': f'Treasure "{treasure_name}" deleted successfully'})
        
    except Treasure.DoesNotExist:
        return Response({'error': 'Treasure not found'}, status=404)