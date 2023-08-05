""" This module provide constants related to the site and default admin user
"""
from .directories import DOT_ENV_CONFIG

SITE_URL: str = DOT_ENV_CONFIG['SITE_URL']
ADMIN_EMAIL: str = DOT_ENV_CONFIG['ADMIN_EMAIL']
ADMIN_USERNAME: str = DOT_ENV_CONFIG['ADMIN_USERNAME'] if 'ADMIN_USERNAME' in DOT_ENV_CONFIG else 'admin'
ADMIN_PASSWORD: str = DOT_ENV_CONFIG['ADMIN_PASSWORD'] if 'ADMIN_PASSWORD' in DOT_ENV_CONFIG else 'admin'
