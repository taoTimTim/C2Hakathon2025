import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Canvas API Configuration
    CANVAS_API_URL = os.getenv('CANVAS_API_URL', 'https://canvas.instructure.com/api/v1')
    CANVAS_BASE_URL = os.getenv('CANVAS_BASE_URL', 'https://canvas.instructure.com')

    # Database Configuration
    DB_NAME = os.getenv('DB_NAME')
    DB_USER = os.getenv('DB_USER')
    DB_PASSWORD = os.getenv('DB_PASSWORD')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = int(os.getenv('DB_PORT', 3306))

    # Server Configuration
    PORT = int(os.getenv('PORT', 5000))
    ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')

    # Session Configuration
    SESSION_TOKEN_EXPIRY = int(os.getenv('SESSION_TOKEN_EXPIRY', 86400))  # 24 hours in seconds

    # Canvas Sync Configuration
    SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', 3600))  # 1 hour in seconds
    AUTO_SYNC_ENABLED = os.getenv('AUTO_SYNC_ENABLED', 'true').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

def get_config():
    """Get the appropriate configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
