"""Dashboard summary route – /api/dashboard"""
from flask import Blueprint, jsonify, session, request
from database import db
from models import Ticket, Asset, User, Announcement, AuditLog, Notification

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/summary', methods=['GET'])
def summary():
    # Ticket stats
    open_tickets      = Ticket.query.filter_by(status='open').count()
    in_progress       = Ticket.query.filter_by(status='in_progress').count()
    resolved_tickets  = Ticket.query.filter_by(status='resolved').count()
    critical_tickets  = Ticket.query.filter(Ticket.priority=='critical',
                                            Ticket.status.in_(['open','in_progress'])).count()

    # Ticket category breakdown
    categories = {}
    for cat in ['hardware','software','network','account','other']:
        categories[cat] = Ticket.query.filter_by(category=cat).count()

    # Asset stats
    total_assets      = Asset.query.count()
    active_assets     = Asset.query.filter_by(status='active').count()
    maintenance_assets= Asset.query.filter_by(status='maintenance').count()

    # User stats
    total_users       = User.query.filter_by(is_active=True).count()

    # Recent tickets
    recent_tickets = [t.to_dict() for t in
                      Ticket.query.order_by(Ticket.created_at.desc()).limit(5).all()]

    # Recent activity (audit log)
    recent_activity = [a.to_dict() for a in
                       AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()]

    # Active announcements
    announcements = [a.to_dict() for a in
                     Announcement.query.filter_by(is_published=True)
                     .order_by(Announcement.created_at.desc()).limit(3).all()]

    return jsonify({
        'tickets': {
            'open':       open_tickets,
            'in_progress':in_progress,
            'resolved':   resolved_tickets,
            'critical':   critical_tickets,
            'by_category':categories,
        },
        'assets': {
            'total':      total_assets,
            'active':     active_assets,
            'maintenance':maintenance_assets,
        },
        'users':          {'total': total_users},
        'recent_tickets': recent_tickets,
        'recent_activity':recent_activity,
        'announcements':  announcements,
    }), 200


@dashboard_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Get user's notifications"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    notifications = Notification.query.filter_by(user_id=user_id)\
        .order_by(Notification.created_at.desc()).all()
    
    return jsonify([n.to_dict() for n in notifications]), 200


@dashboard_bp.route('/notifications/<int:notif_id>/read', methods=['PUT'])
def mark_notification_read(notif_id):
    """Mark notification as read"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    notification = Notification.query.get_or_404(notif_id)
    
    # Only user who owns the notification can mark it as read
    if notification.user_id != user_id:
        return jsonify({'error': 'Access denied'}), 403
    
    notification.is_read = True
    db.session.commit()
    
    return jsonify(notification.to_dict()), 200


@dashboard_bp.route('/notifications/unread-count', methods=['GET'])
def unread_notification_count():
    """Get count of unread notifications"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Authentication required'}), 401
    
    count = Notification.query.filter_by(user_id=user_id, is_read=False).count()
    return jsonify({'unread_count': count}), 200
