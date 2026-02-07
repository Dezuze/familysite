import os
import sys

# Set the path to the project directory
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Set the settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backapi.settings')

# Import the WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
