"""Announcements routes – /api/announcements"""
from flask import Blueprint, request, jsonify, session
from database import db
from models import Announcement, User
from datetime import datetime

announce_bp = Blueprint('announcements', __name__)

def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None

@announce_bp.route('/', methods=['GET'])
def list_announcements():
    q = Announcement.query.filter_by(is_published=True)
    if request.args.get('priority'): q = q.filter_by(priority=request.args['priority'])
    return jsonify([a.to_dict() for a in q.order_by(Announcement.created_at.desc()).all()]), 200

@announce_bp.route('/', methods=['POST'])
def create_announcement():
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    data = request.get_json()
    a = Announcement(
        title=data['title'], content=data['content'],
        author_id=user.id, priority=data.get('priority','normal'),
        is_published=data.get('is_published', True),
        expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
    )
    db.session.add(a)
    db.session.commit()
    return jsonify(a.to_dict()), 201

@announce_bp.route('/<int:ann_id>', methods=['GET'])
def get_announcement(ann_id):
    ann = Announcement.query.get_or_404(ann_id)
    user = current_user()
    # Non-staff users can only read published announcements
    if not user or user.role.name not in ('admin', 'it_staff'):
        if not ann.is_published:
            return jsonify({'error': 'Access denied'}), 403
    return jsonify(ann.to_dict()), 200

@announce_bp.route('/<int:ann_id>', methods=['PUT'])
def update_announcement(ann_id):
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403
    ann = Announcement.query.get_or_404(ann_id)
    data = request.get_json()
    for f in ['title','content','priority','is_published']:
        if f in data: setattr(ann, f, data[f])
    if data.get('expires_at'): ann.expires_at = datetime.fromisoformat(data['expires_at'])
    db.session.commit()
    return jsonify(ann.to_dict()), 200

@announce_bp.route('/<int:ann_id>', methods=['DELETE'])
def delete_announcement(ann_id):
    user = current_user()
    if not user or user.role.name != 'admin':
        return jsonify({'error': 'Admin only'}), 403
    ann = Announcement.query.get_or_404(ann_id)
    db.session.delete(ann)
    db.session.commit()
    return jsonify({'message': 'Announcement deleted'}), 200
