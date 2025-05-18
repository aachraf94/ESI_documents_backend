"""
WSGI config for ESI_document_project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ESI_document_project.settings")

# Apply production settings if we're on Render or in production mode
if os.environ.get('RENDER') or os.environ.get('DJANGO_ENV') == 'production':
    try:
        from ESI_document_project import production
        import django.conf as conf
        for setting in dir(production):
            if setting.isupper():
                setattr(conf.settings, setting, getattr(production, setting))
        print("✅ Production settings applied")
    except ImportError:
        print("⚠️ Could not import production settings")

application = get_wsgi_application()
