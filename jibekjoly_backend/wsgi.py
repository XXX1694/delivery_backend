import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jibekjoly_backend.settings.production')

application = get_wsgi_application()