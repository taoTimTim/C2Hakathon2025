from flask import Flask
from flask_socketio import SocketIO
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# In main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",   # Your local API
        "http://127.0.0.1:8000",   # Alternative local access
        "https://canvas.ubc.ca",   # ⬅️ CRITICAL: The site your extension lives on
        # Add the UBC Canvas dev/staging site if you have one.
    ],
    # ... rest of your CORS settings ...
)

# Configure CORS
CORS(app, resources={
    r"/api/*": {
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "PUT", "DELETE"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/recommend": {
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    },
    r"/items": {
        "origins": os.getenv('ALLOWED_ORIGINS', '*').split(','),
        "methods": ["GET", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Initialize SocketIO
socketio = SocketIO(
    app,
    cors_allowed_origins=os.getenv('ALLOWED_ORIGINS', '*').split(','),
    async_mode='eventlet',
    logger=True,
    engineio_logger=True
)

# Import and register routes
from routes import auth, chat, canvas_sync, recommendation

app.register_blueprint(auth.bp)
app.register_blueprint(chat.bp)
app.register_blueprint(canvas_sync.bp)
app.register_blueprint(recommendation.bp)

# Import socket event handlers
from socket_events import connection_events, message_events, room_events

# Register socket event handlers
connection_events.register_handlers(socketio)
message_events.register_handlers(socketio)
room_events.register_handlers(socketio)

# Health check endpoint
@app.route('/')
def health_check():
    return {"status": "ok", "message": "Canvas Chat Server Running"}

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return {"error": "Not found"}, 404

@app.errorhandler(500)
def internal_error(error):
    return {"error": "Internal server error"}, 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    print(f"Starting Canvas Chat Server on port {port}")
    print(f"Debug mode: {debug}")

    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=debug
    )
