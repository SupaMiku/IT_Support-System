"""Users routes – /api/users"""
from flask import Blueprint, request, jsonify, session
from werkzeug.security import generate_password_hash
from database import db
from models import User, Role

users_bp = Blueprint('users', __name__)

def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None

@users_bp.route('/', methods=['GET'])
def list_users():
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    q = User.query
    if request.args.get('role'):       q = q.join(Role).filter(Role.name == request.args['role'])
    if request.args.get('department'): q = q.filter(User.department.ilike(f"%{request.args['department']}%"))
    if request.args.get('is_active'):  q = q.filter(User.is_active == (request.args['is_active'].lower() == 'true'))
    return jsonify([u.to_dict() for u in q.order_by(User.full_name).all()]), 200

@users_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    user = current_user()
    if not user or (user.id != user_id and user.role.name not in ('admin','it_staff')):
        return jsonify({'error': 'Insufficient permissions'}), 403
    target = User.query.get_or_404(user_id)
    return jsonify(target.to_dict()), 200

@users_bp.route('/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = current_user()
    if not user or (user.id != user_id and user.role.name != 'admin'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    target = User.query.get_or_404(user_id)
    data   = request.get_json()
    for f in ['full_name', 'department', 'phone']:
        if f in data: setattr(target, f, data[f])
    if data.get('password') and (user.id == user_id or user.role.name == 'admin'):
        target.password_hash = generate_password_hash(data['password'])
    if 'is_active' in data and user.role.name == 'admin':
        target.is_active = data['is_active']
    db.session.commit()
    return jsonify(target.to_dict()), 200

@users_bp.route('/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = current_user()
    if not user or user.role.name != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    target = User.query.get_or_404(user_id)
    target.is_active = False   # soft delete
    db.session.commit()
    return jsonify({'message': 'User deactivated'}), 200

@users_bp.route('/staff', methods=['GET'])
def list_staff():
    """Get all IT staff members for assignment purposes"""
    staff_role = Role.query.filter_by(name='it_staff').first()
    admin_role = Role.query.filter_by(name='admin').first()
    
    staff = User.query.filter(
        User.is_active == True,
        ((User.role_id == staff_role.id if staff_role else False) or 
         (User.role_id == admin_role.id if admin_role else False))
    ).order_by(User.full_name).all()
    
    return jsonify([{'id': u.id, 'full_name': u.full_name} for u in staff]), 200

@users_bp.route('/roles', methods=['GET'])
def list_roles():
    return jsonify([r.to_dict() for r in Role.query.all()]), 200
