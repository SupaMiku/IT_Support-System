"""
Auth routes – /api/auth
  POST /register
  POST /login
  POST /logout
  GET  /me
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models import User, Role, AuditLog
from datetime import datetime

auth_bp = Blueprint('auth', __name__)


def log_action(user_id, action, details=None):
    entry = AuditLog(
        user_id=user_id, action=action,
        target_type='User', target_id=user_id,
        details=details,
        ip_address=request.remote_addr
    )
    db.session.add(entry)


@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    required = ['email', 'password', 'full_name']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    email = data['email'].strip()
    full_name = data['full_name'].strip()
    password = data['password']

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 409

    # Generate username from email (everything before @)
    username = email.split('@')[0]
    
    # If username exists, append a number
    if User.query.filter_by(username=username).first():
        counter = 1
        while User.query.filter_by(username=f"{username}{counter}").first():
            counter += 1
        username = f"{username}{counter}"

    # Get role from request, default to student
    role_name = data.get('role', 'student')
    print(f"[REGISTER DEBUG] Received role: {role_name}")
    
    role = Role.query.filter_by(name=role_name).first()
    print(f"[REGISTER DEBUG] Role lookup result: {role}")
    if role:
        print(f"[REGISTER DEBUG] Found role: {role.name} (id={role.id})")
    
    if not role:
        return jsonify({'error': 'Invalid role'}), 400

    user = User(
        username=username,
        email=email,
        password_hash=generate_password_hash(password),
        full_name=full_name,
        role_id=role.id,
        department=data.get('department'),
        phone=data.get('phone'),
    )
    print(f"[REGISTER DEBUG] Creating user: {username} with role_id={role.id} (role={role.name})")
    db.session.add(user)
    db.session.flush()
    print(f"[REGISTER DEBUG] User created with id={user.id}")
    log_action(user.id, 'auth.register')
    db.session.commit()

    print(f"[REGISTER DEBUG] Registration complete. User role_id={user.role_id}")
    return jsonify({'message': 'Account created successfully', 'user': user.to_dict()}), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = User.query.filter_by(email=data['email']).first()
    if not user or not check_password_hash(user.password_hash, data['password']):
        return jsonify({'error': 'Invalid credentials'}), 401
    if not user.is_active:
        return jsonify({'error': 'Account is deactivated'}), 403

    print(f"[LOGIN DEBUG] User login: {user.email}, role_id={user.role_id}, role={user.role.name}")
    user.last_login = datetime.utcnow()
    session['user_id'] = user.id
    log_action(user.id, 'auth.login')
    db.session.commit()

    return jsonify({'message': 'Login successful', 'user': user.to_dict()}), 200


@auth_bp.route('/logout', methods=['POST'])
def logout():
    user_id = session.pop('user_id', None)
    if user_id:
        log_action(user_id, 'auth.logout')
        db.session.commit()
    return jsonify({'message': 'Logged out'}), 200


@auth_bp.route('/me', methods=['GET'])
def me():
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Not authenticated'}), 401
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify(user.to_dict()), 200
