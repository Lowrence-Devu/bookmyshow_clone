"""
Vercel serverless function entry point for Django.
"""
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bookmyseat.settings')

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
app = application
