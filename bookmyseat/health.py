"""Health check endpoint for verifying database connectivity."""
from django.http import JsonResponse
from django.db import connection

def health_check(request):
    """Check if database is connected and responsive."""
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        # Get database info
        db_name = connection.settings_dict.get('NAME', 'unknown')
        db_host = connection.settings_dict.get('HOST', 'unknown')
        
        return JsonResponse({
            'status': 'healthy',
            'database': 'connected',
            'db_name': db_name if 'db.sqlite3' not in str(db_name) else 'SQLite (local)',
            'db_host': db_host,
            'message': 'Database connection successful'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'message': 'Database connection failed'
        }, status=500)
