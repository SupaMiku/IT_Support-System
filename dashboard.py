"""Dashboard summary route – /api/dashboard"""
from flask import Blueprint, jsonify, session
from database import db
from models import Ticket, Asset, User, Announcement, AuditLog

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