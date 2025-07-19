from flask import Flask, send_from_directory
from flask_cors import CORS
import os
import sys
from datetime import timedelta
from src.extensions import db, migrate

def create_app(for_migrations=False):
    """Factory function to create Flask app"""
    app = Flask(__name__, static_folder='static')
    
    # Create full path to the instance directory and ensure it exists
    instance_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'instance'))
    os.makedirs(instance_dir, exist_ok=True)

    # Set absolute path for SQLite database
    db_path = os.path.join(instance_dir, 'stylemate.db')
    
    # Configuration
    app.config['SECRET_KEY'] = 'stylemate-secret-key-change-in-production'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    if for_migrations:
        return app
        
    # Enable CORS for all routes
    CORS(app, supports_credentials=True, origins=['*'])
    print("✅ Starting app setup...")

    # Create database tables and initialize data
    with app.app_context():
        try:
            from src.models.user import User
            from src.models.favorite import Favorite
            
            db.create_all()
            print("✅ Database tables created/verified")
            
            from src.models.user import init_db as init_user_db
            init_user_db(app)
            print("✅ User database initialized")
        except Exception as e:
            print(f"❌ Database setup failed: {str(e)}")

    # Register blueprints
    blueprints = {
        'auth': 'src.routes.auth',
        'analysis': 'src.routes.analysis',
        'favorites': 'src.routes.favorites',
        'blog': 'src.routes.blog',
        'user': 'src.routes.user'
    }

    for name, module_path in blueprints.items():
        try:
            module = __import__(module_path, fromlist=[f'{name}_bp'])
            bp_names = [f'{name}_bp', f'{name}s_bp', name]
            bp = None
            
            for bp_name in bp_names:
                if hasattr(module, bp_name):
                    bp = getattr(module, bp_name)
                    break
            
            if bp:
                app.register_blueprint(bp)
                print(f"✅ {name.capitalize()} blueprint registered")
            else:
                print(f"❌ {name.capitalize()} blueprint not found in module")
        except ImportError as e:
            print(f"⚠️ {name.capitalize()} module not found: {str(e)}")
        except Exception as e:
            print(f"❌ {name.capitalize()} blueprint failed: {str(e)}")

    # Frontend routes
    @app.route('/')
    def index():
        return send_from_directory('static', 'index.html')

    @app.route('/signup.html')
    def signup():
        return send_from_directory('static', 'signup.html')

    @app.route('/signin.html')
    def signin():
        return send_from_directory('static', 'signin.html')

    @app.route('/analysis.html')
    def analysis():
        return send_from_directory('static', 'analysis.html')

    @app.route('/dashboard.html')
    def dashboard():
        return send_from_directory('static', 'dashboard.html')

    @app.route('/output.html')
    def output():
        return send_from_directory('static', 'output.html')

    @app.route('/favorites.html')
    def favorites():
        return send_from_directory('static', 'favorites.html')

    @app.route('/blog.html')
    def blog():
        return send_from_directory('static', 'blog.html')

    @app.route('/<path:filename>')
    def static_files(filename):
        return send_from_directory('static', filename)

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        from flask import jsonify, request
        if request.path.startswith('/api/'):
            return jsonify({"status": "error", "message": "API endpoint not found"}), 404
        return send_from_directory('static', 'index.html')

    @app.errorhandler(500)
    def internal_error(error):
        from flask import jsonify, request
        db.session.rollback()
        if request.path.startswith('/api/'):
            return jsonify({"status": "error", "message": "Internal server error"}), 500
        return send_from_directory('static', 'index.html')

    # Health check
    @app.route('/api/health')
    def health_check():
        from flask import jsonify
        return jsonify({"status": "ok", "message": "StyleMate API is running"})

    # User session check
    @app.route('/api/auth/status')
    def auth_status():
        from flask import jsonify, session
        from src.models.user import User
        
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user and user.is_active:
                return jsonify({
                    "status": "authenticated",
                    "user": user.to_dict()
                })
        
        return jsonify({"status": "anonymous"})

    return app

# Check if this is a migration command
is_migration_command = 'db' in sys.argv

# Create app instance
app = create_app(for_migrations=is_migration_command)

# Run the server if not in migration mode
if not is_migration_command and (__name__ == '__main__' or __name__ == 'src.main'):
    STATIC_DIR = os.path.join(os.path.dirname(__file__), 'static')
    expected_path = os.path.join(STATIC_DIR, "Dress", "Female", "GOWN", "RED", "2085.jpeg")
    
    print("STATIC_DIR:", STATIC_DIR)
    print("Expected Path:", expected_path)
    print("Exists?", os.path.exists(expected_path))
    
    print("🚀 Running StyleMate on http://127.0.0.1:5001")
    app.run(debug=True, host='0.0.0.0', port=5001)
