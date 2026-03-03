"""
Tickets routes – /api/tickets
  GET    /               – list all tickets (with filters)
  POST   /               – create ticket
  GET    /<id>           – get single ticket
  PUT    /<id>           – update ticket
  DELETE /<id>           – delete ticket
  POST   /<id>/comments  – add comment
  GET    /<id>/comments  – list comments
"""

from flask import Blueprint, request, jsonify, session
from database import db
from models import Ticket, TicketComment, User, AuditLog, Notification
from datetime import datetime

tickets_bp = Blueprint('tickets', __name__)


def current_user():
    uid = session.get('user_id')
    return User.query.get(uid) if uid else None


def log_action(user_id, action, target_id=None, details=None):
    db.session.add(AuditLog(
        user_id=user_id, action=action, target_type='Ticket',
        target_id=target_id, details=details,
        ip_address=request.remote_addr
    ))


def notify(user_id, title, message, link=None):
    db.session.add(Notification(
        user_id=user_id, title=title, message=message, link=link
    ))


# ── List / Create ──────────────────────────────────────────────────
@tickets_bp.route('/', methods=['GET'])
def list_tickets():
    q = Ticket.query

    status   = request.args.get('status')
    priority = request.args.get('priority')
    category = request.args.get('category')
    assigned = request.args.get('assigned_to')

    if status:   q = q.filter(Ticket.status   == status)
    if priority: q = q.filter(Ticket.priority == priority)
    if category: q = q.filter(Ticket.category == category)
    if assigned: q = q.filter(Ticket.assigned_to_id == int(assigned))

    tickets = q.order_by(Ticket.created_at.desc()).all()
    return jsonify([t.to_dict() for t in tickets]), 200


@tickets_bp.route('/', methods=['POST'])
def create_ticket():
    user = current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    data = request.get_json()
    if not data.get('title') or not data.get('description'):
        return jsonify({'error': 'Title and description are required'}), 400

    ticket = Ticket(
        title=data['title'],
        description=data['description'],
        category=data.get('category', 'other'),
        priority=data.get('priority', 'medium'),
        location=data.get('location'),
        requester_id=user.id,
        assigned_to_id=data.get('assigned_to_id'),
        due_date=datetime.fromisoformat(data['due_date']) if data.get('due_date') else None,
    )
    db.session.add(ticket)
    db.session.flush()
    log_action(user.id, 'ticket.create', target_id=ticket.id, details=data['title'])

    # Notify assigned staff
    if ticket.assigned_to_id:
        notify(ticket.assigned_to_id,
               f'New ticket assigned: #{ticket.id}',
               ticket.title,
               link=f'/tickets/{ticket.id}')

    db.session.commit()
    return jsonify(ticket.to_dict()), 201


# ── Single ticket ──────────────────────────────────────────────────
@tickets_bp.route('/<int:ticket_id>', methods=['GET'])
def get_ticket(ticket_id):
    ticket = Ticket.query.get_or_404(ticket_id)
    return jsonify(ticket.to_dict()), 200


@tickets_bp.route('/<int:ticket_id>', methods=['PUT'])
def update_ticket(ticket_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    ticket = Ticket.query.get_or_404(ticket_id)
    data   = request.get_json()

    for field in ['title', 'description', 'category', 'priority', 'status', 'location', 'assigned_to_id']:
        if field in data:
            setattr(ticket, field, data[field])

    if data.get('status') == 'resolved' and not ticket.resolved_at:
        ticket.resolved_at = datetime.utcnow()

    if data.get('due_date'):
        ticket.due_date = datetime.fromisoformat(data['due_date'])

    log_action(user.id, 'ticket.update', target_id=ticket.id, details=str(data))
    notify(ticket.requester_id,
           f'Ticket #{ticket.id} updated',
           f'Status changed to {ticket.status}',
           link=f'/tickets/{ticket.id}')

    db.session.commit()
    return jsonify(ticket.to_dict()), 200


@tickets_bp.route('/<int:ticket_id>', methods=['DELETE'])
def delete_ticket(ticket_id):
    user = current_user()
    if not user or user.role.name not in ('admin', 'it_staff'):
        return jsonify({'error': 'Insufficient permissions'}), 403

    ticket = Ticket.query.get_or_404(ticket_id)
    log_action(user.id, 'ticket.delete', target_id=ticket.id, details=ticket.title)
    db.session.delete(ticket)
    db.session.commit()
    return jsonify({'message': f'Ticket #{ticket_id} deleted'}), 200


# ── Comments ───────────────────────────────────────────────────────
@tickets_bp.route('/<int:ticket_id>/comments', methods=['GET'])
def list_comments(ticket_id):
    ticket   = Ticket.query.get_or_404(ticket_id)
    user     = current_user()
    is_staff = user and user.role.name in ('admin', 'it_staff')

    comments = ticket.comments
    if not is_staff:
        comments = comments.filter_by(is_internal=False)

    return jsonify([c.to_dict() for c in comments.order_by(TicketComment.created_at).all()]), 200


@tickets_bp.route('/<int:ticket_id>/comments', methods=['POST'])
def add_comment(ticket_id):
    user = current_user()
    if not user:
        return jsonify({'error': 'Authentication required'}), 401

    ticket = Ticket.query.get_or_404(ticket_id)
    data   = request.get_json()

    if not data.get('content'):
        return jsonify({'error': 'Comment content required'}), 400

    is_staff   = user.role.name in ('admin', 'it_staff')
    is_internal= bool(data.get('is_internal')) and is_staff

    comment = TicketComment(
        ticket_id=ticket_id,
        author_id=user.id,
        content=data['content'],
        is_internal=is_internal
    )
    db.session.add(comment)
    log_action(user.id, 'ticket.comment', target_id=ticket_id)

    # Notify requester (if comment is not internal)
    if not is_internal and ticket.requester_id != user.id:
        notify(ticket.requester_id,
               f'New comment on Ticket #{ticket_id}',
               data['content'][:100],
               link=f'/tickets/{ticket_id}')

    db.session.commit()
    return jsonify(comment.to_dict()), 201