from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.db import connection

@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    db_status = 'unknown'
    http_status = 200
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            db_status = 'up'
    except Exception:
        db_status = 'down'
        http_status = 503
    return Response({"api": "up", "db": db_status}, status=http_status)