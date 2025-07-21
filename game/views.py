from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Treasure, Player, Discovery
import math

@api_view(['GET'])
@permission_classes([AllowAny])
def get_nearby_treasures(request):
    try:
        lat = float(request.GET.get('lat'))
        lng = float(request.GET.get('lng'))
    except (TypeError, ValueError):
        return Response({'error': 'Invalid coordinates'}, status=400)
    
    treasures = Treasure.objects.filter(is_active=True)
    nearby = []
    
    for treasure in treasures:
        distance = calculate_distance(lat, lng, treasure.latitude, treasure.longitude)
        if distance <= treasure.discovery_radius:
            nearby.append({
                'id': treasure.id,
                'name': treasure.name,
                'description': treasure.description,
                'latitude': treasure.latitude,
                'longitude': treasure.longitude,
                'points': treasure.points,
                'distance': round(distance, 2)
            })
    
    return Response(nearby)

@api_view(['POST'])
@permission_classes([AllowAny])
def discover_treasure(request):
    try:
        treasure_id = request.data.get('treasure_id')
        player_lat = float(request.data.get('latitude'))
        player_lng = float(request.data.get('longitude'))
        
        treasure = Treasure.objects.get(id=treasure_id)
        
        # Create anonymous player if no user
        if request.user.is_anonymous:
            session_key = request.session.session_key
            if not session_key:
                request.session.create()
                session_key = request.session.session_key
            
            username = f"Guest_{session_key[:8]}"
            user, created = User.objects.get_or_create(username=username)
        else:
            user = request.user
            
        player, created = Player.objects.get_or_create(user=user)
        
        # Verify distance
        distance = calculate_distance(player_lat, player_lng, treasure.latitude, treasure.longitude)
        if distance > treasure.discovery_radius:
            return Response({'error': 'Too far from treasure'}, status=400)
        
        # Check if already discovered
        if Discovery.objects.filter(player=player, treasure=treasure).exists():
            return Response({'error': 'Already discovered'}, status=400)
        
        # Create discovery
        Discovery.objects.create(
            player=player,
            treasure=treasure,
            player_latitude=player_lat,
            player_longitude=player_lng
        )
        
        # Update player score
        player.total_score += treasure.points
        player.treasures_found += 1
        player.save()
        
        return Response({
            'message': 'Treasure discovered!',
            'points_earned': treasure.points,
            'total_score': player.total_score
        })
        
    except Treasure.DoesNotExist:
        return Response({'error': 'Treasure not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
@permission_classes([AllowAny])
def leaderboard(request):
    top_players = Player.objects.order_by('-total_score')[:10]
    data = [{
        'username': p.user.username,
        'total_score': p.total_score,
        'treasures_found': p.treasures_found
    } for p in top_players]
    return Response(data)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_all_treasures(request):
    treasures = Treasure.objects.all()
    data = [{
        'id': t.id,
        'name': t.name,
        'description': t.description,
        'latitude': t.latitude,
        'longitude': t.longitude,
        'points': t.points,
        'is_active': t.is_active,
        'discovery_radius': t.discovery_radius
    } for t in treasures]
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_treasure(request):
    try:
        treasure = Treasure.objects.create(
            name=request.data.get('name'),
            description=request.data.get('description', ''),
            latitude=float(request.data.get('latitude')),
            longitude=float(request.data.get('longitude')),
            points=int(request.data.get('points', 100)),
            discovery_radius=float(request.data.get('radius', 50.0))
        )
        return Response({'id': treasure.id, 'message': 'Treasure created'})
    except Exception as e:
        return Response({'error': str(e)}, status=400)

def calculate_distance(lat1, lng1, lat2, lng2):
    """Calculate distance between two points in meters using Haversine formula"""
    R = 6371000  # Earth's radius in meters
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lng = math.radians(lng2 - lng1)
    
    a = (math.sin(delta_lat/2)**2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lng/2)**2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c
