from src.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Use string-based relationship to avoid circular imports
    favorites = db.relationship(
        'Favorite', 
        backref='user', 
        lazy=True, 
        cascade='all, delete-orphan'
    )
    
    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email.lower()
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def to_dict(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'full_name': self.get_full_name(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'is_active': self.is_active
        }
    
    def __repr__(self):
        return f'<User {self.email}>'

def init_db(app):
    """Initialize the database with the Flask app"""
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Create demo user
        demo_user = User.query.filter_by(email='demo@stylemate.com').first()
        if not demo_user:
            demo_user = User(
                first_name='Demo',
                last_name='User',
                email='demo@stylemate.com',
                password='demo123'
            )
            db.session.add(demo_user)
            db.session.commit()
            print("Demo user created: demo@stylemate.com / demo123")