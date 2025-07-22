# 1. Create missing static directory
mkdir -p treasure_hunt/static

# 2. Create a railway.json for configuration
cat > railway.json << 'EOF'
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "healthcheckPath": "/health/",
    "healthcheckTimeout": 100,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
EOF

# 3. Update settings.py with proper configuration
cat > treasure_hunt/treasure_hunt/settings.py << 'EOF'
"""
Django settings for treasure_hunt project.
"""
import os
import dj_database_url
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings - Use environment variables
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-zpy!ksv%^^i*rdnj7o#4uv*vjs_8e6#0=wl$ougvx)1u6@jm2l')
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'

# Allowed hosts - Support Railway domains
ALLOWED_HOSTS = ['*']  # For debugging, restrict this later
RAILWAY_STATIC_URL = os.environ.get('RAILWAY_STATIC_URL')
if RAILWAY_STATIC_URL:
    ALLOWED_HOSTS.append(RAILWAY_STATIC_URL)

# CSRF Trusted Origins for Railway
CSRF_TRUSTED_ORIGINS = []
if os.environ.get('RAILWAY_ENVIRONMENT'):
    CSRF_TRUSTED_ORIGINS = [
        'https://*.up.railway.app',
        'https://*.railway.app'
    ]

# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'rest_framework',
    'corsheaders',
    'game',
    'admin_panel',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = "treasure_hunt.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR,'templates')],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "treasure_hunt.wsgi.application"

# Database - Use Railway's database URL if available
DATABASES = {
    'default': dj_database_url.config(
        default=f'sqlite:///{BASE_DIR}/db.sqlite3',
        conn_max_age=600,
        conn_health_checks=True,
    )
}

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.AllowAny',
    ]
}

# CORS settings
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# Static files configuration
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Only add STATICFILES_DIRS if the static directory exists
static_dir = os.path.join(BASE_DIR, 'static')
if os.path.exists(static_dir):
    STATICFILES_DIRS = [static_dir]

# Whitenoise settings
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Security settings for production
if not DEBUG and os.environ.get('RAILWAY_ENVIRONMENT'):
    # Disable SSL redirect as Railway handles HTTPS
    SECURE_SSL_REDIRECT = False
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
EOF

# 4. Update Procfile for better error handling
cat > treasure_hunt/Procfile << 'EOF'
web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn treasure_hunt.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level info --access-logfile - --error-logfile -
EOF

# 5. Create a simple health check view
cat > treasure_hunt/game/views.py << 'EOF'
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Treasure, Player, Discovery
import math

def health_check(request):
    """Simple health check endpoint"""
    return HttpResponse('OK', status=200)

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
EOF

# 6. Update URLs to include health check
cat > treasure_hunt/game/urls.py << 'EOF'
from django.urls import path
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    # Health check endpoint
    path('health/', views.health_check, name='health_check'),
    
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
EOF

# 7. Create a proper requirements.txt with specific versions
cat > treasure_hunt/requirements.txt << 'EOF'
asgiref==3.8.1
dj-database-url==2.2.0
Django==4.2.16
django-cors-headers==4.4.0
djangorestframework==3.15.2
gunicorn==23.0.0
psycopg2-binary==2.9.10
python-decouple==3.8
sqlparse==0.5.2
whitenoise==6.8.2
EOF

# 8. Update nixpacks.toml for better build process
cat > treasure_hunt/nixpacks.toml << 'EOF'
[build]
cmds = ["pip install --upgrade pip", "pip install -r requirements.txt"]

[start]
cmd = "gunicorn treasure_hunt.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --log-level info --access-logfile - --error-logfile -"

[variables]
NIXPACKS_PYTHON_VERSION = "3.11"
EOF

echo "All fixes applied! Now follow these deployment steps:"
echo "1. Commit these changes to git"
echo "2. Push to your repository"
echo "3. In Railway, set these environment variables:"
echo "   - SECRET_KEY: (generate a new secure key)"
echo "   - DEBUG: False"
echo "   - DATABASE_URL: (Railway provides this automatically if you have a Postgres service)"
echo "4. Redeploy your application"
