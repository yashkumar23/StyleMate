"""
routes/favorites.py
Handle "add / remove favorite" logic for both logged-in and anonymous users.
"""
from flask import Blueprint, request, jsonify, session
from datetime import datetime
import uuid
from src.extensions import db
from src.models.favorite import Favorite
from src.models.user import User

favorites_bp = Blueprint("favorites", __name__, url_prefix="/api/favorites")

SESSION_KEY = "anon_favorites"
MAX_ANON_FAVORITES = 20  # Prevent session from becoming too large

def _get_session_id():
    """Get or create a session ID for anonymous users"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
        session.permanent = True
    return session['session_id']

def _get_current_user():
    """Get current user from session"""
    user_id = session.get('user_id')
    if user_id:
        return User.query.get(user_id)
    return None

def _is_authenticated():
    """Check if user is authenticated"""
    return _get_current_user() is not None

@favorites_bp.route("", methods=["GET"])
def get_favorites():
    """Get all favorites for current user or session"""
    try:
        if _is_authenticated():
            user = _get_current_user()
            favorites = Favorite.query.filter_by(user_id=user.id).all()
        else:
            session_id = _get_session_id()
            favorites = Favorite.query.filter_by(session_id=session_id).all()
        
        return jsonify({
            "status": "ok",
            "favorites": [f.to_dict() for f in favorites]
        })
    except Exception as e:
        print(f"Error getting favorites: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to load favorites"
        }), 500

@favorites_bp.route("/add", methods=["POST"])
def add_favorite():
    """Add a dress to favorites"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error", 
                "message": "No data provided"
            }), 400
        
        required = ['dress_image_url', 'dress_type', 'dress_size']
        if not all(k in data for k in required):
            return jsonify({
                "status": "error", 
                "message": "Missing required fields: " + ", ".join(required)
            }), 400
        
        # Check for duplicates and add favorite
        if _is_authenticated():
            user = _get_current_user()
            existing = Favorite.query.filter_by(
                user_id=user.id,
                dress_image_url=data['dress_image_url'],
                dress_type=data['dress_type'],
                dress_size=data['dress_size']
            ).first()
            
            if existing:
                return jsonify({
                    "status": "exists", 
                    "message": "Already in favorites",
                    "favorite": existing.to_dict()
                })
                
            new_fav = Favorite(
                user_id=user.id,
                dress_image_url=data['dress_image_url'],
                dress_type=data['dress_type'],
                dress_size=data['dress_size'],
                dress_id=data.get('dress_id'),
                created_at=datetime.utcnow()
            )
        else:
            session_id = _get_session_id()
            existing = Favorite.query.filter_by(
                session_id=session_id,
                dress_image_url=data['dress_image_url'],
                dress_type=data['dress_type'],
                dress_size=data['dress_size']
            ).first()
            
            if existing:
                return jsonify({
                    "status": "exists", 
                    "message": "Already in favorites",
                    "favorite": existing.to_dict()
                })
            
            # Check limit for anonymous users
            count = Favorite.query.filter_by(session_id=session_id).count()
            if count >= MAX_ANON_FAVORITES:
                return jsonify({
                    "status": "error", 
                    "message": "Favorites limit reached. Sign in to save more."
                }), 400
                
            new_fav = Favorite(
                session_id=session_id,
                dress_image_url=data['dress_image_url'],
                dress_type=data['dress_type'],
                dress_size=data['dress_size'],
                dress_id=data.get('dress_id'),
                created_at=datetime.utcnow()
            )
        
        db.session.add(new_fav)
        db.session.commit()
        
        return jsonify({
            "status": "ok", 
            "favorite": new_fav.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error adding favorite: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to add favorite"
        }), 500

@favorites_bp.route("/remove/<favorite_id>", methods=["POST", "DELETE"])
def remove_favorite(favorite_id):
    """Remove a favorite by ID"""
    try:
        if _is_authenticated():
            user = _get_current_user()
            fav = Favorite.query.filter_by(id=favorite_id, user_id=user.id).first()
        else:
            session_id = _get_session_id()
            fav = Favorite.query.filter_by(id=favorite_id, session_id=session_id).first()
        
        if not fav:
            return jsonify({
                "status": "error", 
                "message": "Favorite not found"
            }), 404
        
        db.session.delete(fav)
        db.session.commit()
        
        return jsonify({"status": "ok"})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error removing favorite: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to remove favorite"
        }), 500

@favorites_bp.route("/toggle", methods=["POST"])
def toggle_favorite():
    """Toggle favorite status for a dress"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "status": "error", 
                "message": "No data provided"
            }), 400
        
        required = ['dress_image_url', 'dress_type', 'dress_size']
        if not all(k in data for k in required):
            return jsonify({
                "status": "error", 
                "message": "Missing required fields"
            }), 400
        
        # Find existing favorite
        if _is_authenticated():
            user = _get_current_user()
            existing = Favorite.query.filter_by(
                user_id=user.id,
                dress_image_url=data['dress_image_url'],
                dress_type=data['dress_type'],
                dress_size=data['dress_size']
            ).first()
        else:
            session_id = _get_session_id()
            existing = Favorite.query.filter_by(
                session_id=session_id,
                dress_image_url=data['dress_image_url'],
                dress_type=data['dress_type'],
                dress_size=data['dress_size']
            ).first()
        
        if existing:
            # Remove from favorites
            db.session.delete(existing)
            db.session.commit()
            return jsonify({
                "status": "removed",
                "message": "Removed from favorites"
            })
        else:
            # Add to favorites
            if not _is_authenticated():
                session_id = _get_session_id()
                count = Favorite.query.filter_by(session_id=session_id).count()
                if count >= MAX_ANON_FAVORITES:
                    return jsonify({
                        "status": "error", 
                        "message": "Favorites limit reached. Sign in to save more."
                    }), 400
            
            new_fav = Favorite(
                user_id=_get_current_user().id if _is_authenticated() else None,
                session_id=None if _is_authenticated() else _get_session_id(),
                dress_image_url=data['dress_image_url'],
                dress_type=data['dress_type'],
                dress_size=data['dress_size'],
                dress_id=data.get('dress_id'),
                created_at=datetime.utcnow()
            )
            
            db.session.add(new_fav)
            db.session.commit()
            
            return jsonify({
                "status": "added",
                "message": "Added to favorites",
                "favorite": new_fav.to_dict()
            })
            
    except Exception as e:
        db.session.rollback()
        print(f"Error toggling favorite: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to update favorite"
        }), 500

@favorites_bp.route("/migrate", methods=["POST"])
def migrate_favorites():
    """Migrate anonymous favorites to authenticated user account"""
    try:
        if not _is_authenticated():
            return jsonify({
                "status": "error", 
                "message": "User must be authenticated to migrate favorites"
            }), 401
        
        user = _get_current_user()
        session_id = session.get('session_id')
        
        if not session_id:
            return jsonify({
                "status": "ok", 
                "message": "No anonymous favorites to migrate",
                "migrated": 0
            })
        
        # Get anonymous favorites
        anon_favorites = Favorite.query.filter_by(session_id=session_id).all()
        migrated_count = 0
        
        for fav in anon_favorites:
            # Check if user already has this favorite
            existing = Favorite.query.filter_by(
                user_id=user.id,
                dress_image_url=fav.dress_image_url,
                dress_type=fav.dress_type,
                dress_size=fav.dress_size
            ).first()
            
            if not existing:
                # Migrate the favorite
                fav.user_id = user.id
                fav.session_id = None
                migrated_count += 1
            else:
                # Delete duplicate anonymous favorite
                db.session.delete(fav)
        
        db.session.commit()
        
        # Clear session data
        session.pop('session_id', None)
        
        return jsonify({
            "status": "ok", 
            "message": f"Successfully migrated {migrated_count} favorites",
            "migrated": migrated_count
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error migrating favorites: {str(e)}")
        return jsonify({
            "status": "error", 
            "message": "Failed to migrate favorites"
        }), 500

