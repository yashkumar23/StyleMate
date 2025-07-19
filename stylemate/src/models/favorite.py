from src.extensions import db
from datetime import datetime

class Favorite(db.Model):
    __tablename__ = 'favorites'
    
    id = db.Column(db.Integer, primary_key=True)
    # Restore foreign key constraint now that we have the User model
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    dress_image_url = db.Column(db.String(500), nullable=False)
    dress_type = db.Column(db.String(100), nullable=False)
    dress_size = db.Column(db.String(20), nullable=False)
    dress_id = db.Column(db.String(100), nullable=True)
    # Add session_id for anonymous users
    session_id = db.Column(db.String(100), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Add unique constraints to prevent duplicates
    __table_args__ = (
        db.UniqueConstraint('user_id', 'dress_image_url', 'dress_type', 'dress_size', 
                          name='unique_user_favorite'),
        db.UniqueConstraint('session_id', 'dress_image_url', 'dress_type', 'dress_size', 
                          name='unique_session_favorite'),
    )
    
    def to_dict(self):
        return {
            'id': self.id,
            'dress_image_url': self.dress_image_url,
            'dress_type': self.dress_type,
            'dress_size': self.dress_size,
            'dress_id': self.dress_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
    
    def __repr__(self):
        return f'<Favorite {self.id}: {self.dress_type} for User {self.user_id or "Anonymous"}>'

