"""
Configuration loader - reads from Streamlit secrets or environment variables
Supports both local development and cloud deployment
"""

import os
import streamlit as st


def get_config(key_path, default=None):
    """
    Get configuration value from secrets.toml or environment variables
    
    Args:
        key_path (str): Path to config like "postgres.host" or "admin.password"
        default: Default value if not found
        
    Returns:
        Configuration value or default
    """
    # Try Streamlit secrets first (local development)
    try:
        keys = key_path.split('.')
        value = st.secrets
        for key in keys:
            value = value[key]
        return value
    except (KeyError, FileNotFoundError):
        pass
    
    # Try environment variable (cloud deployment)
    # Convert "postgres.host" to "POSTGRES_HOST"
    env_key = key_path.upper().replace('.', '_')
    return os.environ.get(env_key, default)


def get_database_config():
    """Get database configuration"""
    return {
        'host': get_config('postgres.host', os.getenv('POSTGRES_HOST')),
        'port': get_config('postgres.port', os.getenv('POSTGRES_PORT', '5432')),
        'database': get_config('postgres.database', os.getenv('POSTGRES_DATABASE', 'postgres')),
        'user': get_config('postgres.user', os.getenv('POSTGRES_USER')),
        'password': get_config('postgres.password', os.getenv('POSTGRES_PASSWORD'))
    }


def get_admin_password():
    """Get admin password"""
    return get_config('admin.password', os.getenv('ADMIN_PASSWORD', 'Oma1123581321-'))


def get_merky_fc_credentials():
    """Get Merky FC credentials"""
    return {
        'username': get_config('merky_fc.username', os.getenv('MERKY_FC_USERNAME')),
        'password': get_config('merky_fc.password', os.getenv('MERKY_FC_PASSWORD'))
    }


def get_whatsapp_config():
    """Get WhatsApp configuration"""
    return {
        'group_id': get_config('whatsapp.group_id', os.getenv('WHATSAPP_GROUP_ID', 'CHAjDSd8Tm14QZ4rGrqQxc'))
    }


def get_booking_config():
    """Get booking configuration"""
    return {
        'preferred_time': get_config('booking.preferred_time', os.getenv('BOOKING_PREFERRED_TIME', '19:00')),
        'auto_book_enabled': str(get_config('booking.auto_book_enabled', os.getenv('BOOKING_AUTO_ENABLED', 'true'))).lower() == 'true',
        'half_pitch_threshold': int(get_config('booking.half_pitch_threshold', os.getenv('BOOKING_HALF_PITCH_THRESHOLD', '14'))),
        'full_pitch_threshold': int(get_config('booking.full_pitch_threshold', os.getenv('BOOKING_FULL_PITCH_THRESHOLD', '18')))
    }


def is_production():
    """Check if running in production (Railway, Fly.io, etc.)"""
    # Common environment variables set by cloud platforms
    return any([
        os.getenv('RAILWAY_ENVIRONMENT'),
        os.getenv('FLY_APP_NAME'),
        os.getenv('DIGITALOCEAN_APP'),
        os.getenv('RENDER'),
        not os.path.exists('.streamlit/secrets.toml')
    ])
