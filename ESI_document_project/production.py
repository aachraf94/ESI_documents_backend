"""
Production settings to address security concerns.
This file should be imported at the end of settings.py in production.
"""

import os

# Set this to False in production
DEBUG = False

# Secure cookie settings
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# HTTP Strict Transport Security
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Redirect all non-HTTPS requests to HTTPS
SECURE_SSL_REDIRECT = True

# Use secure SSL/TLS connection
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Prevent clickjacking
X_FRAME_OPTIONS = 'DENY'

# Enable secure content type nosniff
SECURE_CONTENT_TYPE_NOSNIFF = True

# Enable browser XSS protection
SECURE_BROWSER_XSS_FILTER = True

# Set secure referrer policy
SECURE_REFERRER_POLICY = 'same-origin'
