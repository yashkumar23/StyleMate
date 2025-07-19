from flask import Blueprint, request, jsonify, session, redirect, url_for
from ..models.user import User, db
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_password(password):
    """Validate password strength"""
    if len(password) < 6:
        return False, "Password must be at least 6 characters long"
    return True, "Password is valid"

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    """Handle user registration"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'password', 'confirm_password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'{field} is required'
                }), 400
        
        first_name = data['first_name'].strip()
        last_name = data['last_name'].strip()
        email = data['email'].strip().lower()
        password = data['password']
        confirm_password = data["confirm_password"]
        
        # Validate name lengths
        if len(first_name) < 2:
            return jsonify({
                'success': False,
                'message': 'First name must be at least 2 characters'
            }), 400
        
        if len(last_name) < 2:
            return jsonify({
                'success': False,
                'message': 'Last name must be at least 2 characters'
            }), 400
        
        if not validate_email(email):
            return jsonify({
                'success': False,
                'message': 'Please enter a valid email address'
            }), 400
        
        is_valid, message = validate_password(password)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': message
            }), 400
        
        # Validate password confirmation
        if password != confirm_password:
            return jsonify({
                'success': False,
                'message': 'Passwords do not match'
            }), 400
        
        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({
                'success': False,
                'message': 'An account with this email already exists'
            }), 400
        
        # Create new user
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        # Store user in session
        session['user_id'] = new_user.id
        session['user_email'] = new_user.email
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully!',
            'user': new_user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': 'An error occurred during registration'
        }), 500

@auth_bp.route('/api/signin', methods=['POST'])
def signin():
    """Handle user login"""
    try:
        data = request.get_json()
        
        email = data.get('email', '').strip().lower()
        password = data.get('password', '')
        remember_me = data.get('rememberMe', False)
        
        if not email or not password:
            return jsonify({
                'success': False,
                'message': 'Email and password are required'
            }), 400
        
        # Find user by email
        user = User.query.filter_by(email=email).first()
        
        if not user or not user.check_password(password):
            return jsonify({
                'success': False,
                'message': 'Invalid email or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'success': False,
                'message': 'Account is deactivated'
            }), 401
        
        # Store user in session
        session['user_id'] = user.id
        session['user_email'] = user.email
        
        if remember_me:
            session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login successful!',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'An error occurred during login'
        }), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    """Handle user logout"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200

@auth_bp.route('/api/user', methods=['GET'])
def get_current_user():
    """Get current logged-in user"""
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({
            'success': False,
            'message': 'Not authenticated'
        }), 401
    
    user = User.query.get(user_id)
    if not user:
        session.clear()
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    return jsonify({
        'success': True,
        'user': user.to_dict()
    }), 200

@auth_bp.route('/api/check-email', methods=['POST'])
def check_email():
    """Check if email is already registered"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    if not email:
        return jsonify({
            'success': False,
            'message': 'Email is required'
        }), 400
    
    user = User.query.filter_by(email=email).first()
    
    return jsonify({
        'success': True,
        'exists': user is not None
    }), 200

