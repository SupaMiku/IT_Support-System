"""
School IT Support System – Database Models
==========================================
Tables:
  roles                 – user role definitions
  users                 – all system users
  tickets               – IT support tickets
  ticket_comments       – comments/updates on a ticket
  ticket_attachments    – file attachments per ticket
  assets                – hardware/software inventory
  asset_maintenance     – maintenance logs for assets
  knowledge_base        – self-service KB articles
  announcements         – broadcast messages
  notifications         – per-user notification feed
  audit_logs            – immutable action log
"""

from datetime import datetime
from database import db


# ─────────────────────────────────────────────
# ROLES
# ─────────────────────────────────────────────
class Role(db.Model):
    __tablename__ = 'roles'

    id          = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(50), unique=True, nullable=False)   # admin | it_staff | faculty | student
    description = db.Column(db.String(200))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    users = db.relationship('User', back_populates='role', lazy='dynamic')

    def to_dict(self):
        return {'id': self.id, 'name': self.name, 'description': self.description}


# ─────────────────────────────────────────────
# USERS
# ─────────────────────────────────────────────
class User(db.Model):
    __tablename__ = 'users'

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(80),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name     = db.Column(db.String(120), nullable=False)
    role_id       = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)
    department    = db.Column(db.String(100))
    phone         = db.Column(db.String(20))
    is_active     = db.Column(db.Boolean, default=True)
    last_login    = db.Column(db.DateTime)
    created_at    = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at    = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    role                = db.relationship('Role', back_populates='users')
    submitted_tickets   = db.relationship('Ticket', foreign_keys='Ticket.requester_id',   back_populates='requester',  lazy='dynamic')
    assigned_tickets    = db.relationship('Ticket', foreign_keys='Ticket.assigned_to_id', back_populates='assigned_to', lazy='dynamic')
    comments            = db.relationship('TicketComment',        back_populates='author',     lazy='dynamic')
    assets_assigned     = db.relationship('Asset',                back_populates='assigned_to', lazy='dynamic')
    maintenance_logs    = db.relationship('AssetMaintenance',     back_populates='performed_by', lazy='dynamic')
    kb_articles         = db.relationship('KnowledgeBaseArticle', back_populates='author',      lazy='dynamic')
    announcements       = db.relationship('Announcement',         back_populates='author',      lazy='dynamic')
    notifications       = db.relationship('Notification',         back_populates='user',        lazy='dynamic')
    audit_logs          = db.relationship('AuditLog',             back_populates='user',        lazy='dynamic')

    def to_dict(self, include_sensitive=False):
        data = {
            'id':         self.id,
            'username':   self.username,
            'email':      self.email,
            'full_name':  self.full_name,
            'role':       self.role.name if self.role else None,
            'department': self.department,
            'phone':      self.phone,
            'is_active':  self.is_active,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'created_at': self.created_at.isoformat(),
        }
        return data


# ─────────────────────────────────────────────
# TICKETS
# ─────────────────────────────────────────────
class Ticket(db.Model):
    __tablename__ = 'tickets'

    id             = db.Column(db.Integer, primary_key=True)
    title          = db.Column(db.String(200), nullable=False)
    description    = db.Column(db.Text, nullable=False)

    # Category: hardware | software | network | account | other
    category       = db.Column(db.String(50), nullable=False, default='other')

    # Priority: low | medium | high | critical
    priority       = db.Column(db.String(20), nullable=False, default='medium')

    # Status: open | in_progress | on_hold | resolved | closed
    status         = db.Column(db.String(30), nullable=False, default='open')

    location       = db.Column(db.String(100))                  # physical location of issue
    requester_id   = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    resolved_at    = db.Column(db.DateTime, nullable=True)
    due_date       = db.Column(db.DateTime, nullable=True)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    requester   = db.relationship('User', foreign_keys=[requester_id],   back_populates='submitted_tickets')
    assigned_to = db.relationship('User', foreign_keys=[assigned_to_id], back_populates='assigned_tickets')
    comments    = db.relationship('TicketComment',    back_populates='ticket', cascade='all, delete-orphan', lazy='dynamic')
    attachments = db.relationship('TicketAttachment', back_populates='ticket', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id':           self.id,
            'title':        self.title,
            'description':  self.description,
            'category':     self.category,
            'priority':     self.priority,
            'status':       self.status,
            'location':     self.location,
            'requester':    self.requester.full_name if self.requester else None,
            'assigned_to':  self.assigned_to.full_name if self.assigned_to else None,
            'resolved_at':  self.resolved_at.isoformat() if self.resolved_at else None,
            'due_date':     self.due_date.isoformat() if self.due_date else None,
            'created_at':   self.created_at.isoformat(),
            'updated_at':   self.updated_at.isoformat(),
            'comment_count':self.comments.count(),
        }


class TicketComment(db.Model):
    __tablename__ = 'ticket_comments'

    id         = db.Column(db.Integer, primary_key=True)
    ticket_id  = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    author_id  = db.Column(db.Integer, db.ForeignKey('users.id'),   nullable=False)
    content    = db.Column(db.Text, nullable=False)
    is_internal= db.Column(db.Boolean, default=False)          # internal note (staff only)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship('Ticket', back_populates='comments')
    author = db.relationship('User',   back_populates='comments')

    def to_dict(self):
        return {
            'id':          self.id,
            'ticket_id':   self.ticket_id,
            'author':      self.author.full_name if self.author else None,
            'content':     self.content,
            'is_internal': self.is_internal,
            'created_at':  self.created_at.isoformat(),
        }


class TicketAttachment(db.Model):
    __tablename__ = 'ticket_attachments'

    id          = db.Column(db.Integer, primary_key=True)
    ticket_id   = db.Column(db.Integer, db.ForeignKey('tickets.id'), nullable=False)
    filename    = db.Column(db.String(255), nullable=False)
    filepath    = db.Column(db.String(500), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    ticket = db.relationship('Ticket', back_populates='attachments')

    def to_dict(self):
        return {
            'id': self.id, 'ticket_id': self.ticket_id,
            'filename': self.filename, 'uploaded_at': self.uploaded_at.isoformat()
        }


# ─────────────────────────────────────────────
# ASSETS (Inventory)
# ─────────────────────────────────────────────
class Asset(db.Model):
    __tablename__ = 'assets'

    id             = db.Column(db.Integer, primary_key=True)
    asset_tag      = db.Column(db.String(50), unique=True, nullable=False)   # e.g. PC-LAB1-01
    name           = db.Column(db.String(100), nullable=False)

    # Category: computer | laptop | printer | projector | network | server | peripheral | other
    category       = db.Column(db.String(50), nullable=False, default='other')

    brand          = db.Column(db.String(100))
    model          = db.Column(db.String(100))
    serial_number  = db.Column(db.String(100), unique=True)
    specifications = db.Column(db.Text)                         # JSON string or plain text specs

    # Status: active | inactive | maintenance | retired | lost
    status         = db.Column(db.String(30), nullable=False, default='active')

    location       = db.Column(db.String(100))
    assigned_to_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    purchase_date  = db.Column(db.Date)
    purchase_cost  = db.Column(db.Float)
    warranty_expiry= db.Column(db.Date)
    notes          = db.Column(db.Text)
    created_at     = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at     = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    assigned_to  = db.relationship('User',             back_populates='assets_assigned')
    maintenance  = db.relationship('AssetMaintenance', back_populates='asset', cascade='all, delete-orphan', lazy='dynamic')

    def to_dict(self):
        return {
            'id':             self.id,
            'asset_tag':      self.asset_tag,
            'name':           self.name,
            'category':       self.category,
            'brand':          self.brand,
            'model':          self.model,
            'serial_number':  self.serial_number,
            'status':         self.status,
            'location':       self.location,
            'assigned_to':    self.assigned_to.full_name if self.assigned_to else None,
            'purchase_date':  self.purchase_date.isoformat() if self.purchase_date else None,
            'purchase_cost':  self.purchase_cost,
            'warranty_expiry':self.warranty_expiry.isoformat() if self.warranty_expiry else None,
            'created_at':     self.created_at.isoformat(),
        }


class AssetMaintenance(db.Model):
    __tablename__ = 'asset_maintenance'

    id               = db.Column(db.Integer, primary_key=True)
    asset_id         = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    performed_by_id  = db.Column(db.Integer, db.ForeignKey('users.id'),  nullable=False)

    # Type: preventive | repair | upgrade | inspection
    maintenance_type = db.Column(db.String(50), nullable=False, default='repair')
    description      = db.Column(db.Text)
    cost             = db.Column(db.Float, default=0.0)
    scheduled_date   = db.Column(db.Date)
    completed_date   = db.Column(db.Date)

    # Status: scheduled | in_progress | completed | cancelled
    status           = db.Column(db.String(30), default='scheduled')
    created_at       = db.Column(db.DateTime, default=datetime.utcnow)

    asset        = db.relationship('Asset', back_populates='maintenance')
    performed_by = db.relationship('User',  back_populates='maintenance_logs')

    def to_dict(self):
        return {
            'id':               self.id,
            'asset_tag':        self.asset.asset_tag if self.asset else None,
            'performed_by':     self.performed_by.full_name if self.performed_by else None,
            'maintenance_type': self.maintenance_type,
            'description':      self.description,
            'cost':             self.cost,
            'scheduled_date':   self.scheduled_date.isoformat() if self.scheduled_date else None,
            'completed_date':   self.completed_date.isoformat() if self.completed_date else None,
            'status':           self.status,
        }


# ─────────────────────────────────────────────
# KNOWLEDGE BASE
# ─────────────────────────────────────────────
class KnowledgeBaseArticle(db.Model):
    __tablename__ = 'knowledge_base'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    content      = db.Column(db.Text, nullable=False)

    # Category: hardware | software | network | account | general
    category     = db.Column(db.String(50), default='general')

    author_id    = db.Column(db.Integer, db.ForeignKey('users.id'))
    is_published = db.Column(db.Boolean, default=False)
    views        = db.Column(db.Integer, default=0)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship('User', back_populates='kb_articles')

    def to_dict(self):
        return {
            'id':           self.id,
            'title':        self.title,
            'content':      self.content,
            'category':     self.category,
            'author':       self.author.full_name if self.author else None,
            'is_published': self.is_published,
            'views':        self.views,
            'created_at':   self.created_at.isoformat(),
            'updated_at':   self.updated_at.isoformat(),
        }


# ─────────────────────────────────────────────
# ANNOUNCEMENTS
# ─────────────────────────────────────────────
class Announcement(db.Model):
    __tablename__ = 'announcements'

    id           = db.Column(db.Integer, primary_key=True)
    title        = db.Column(db.String(200), nullable=False)
    content      = db.Column(db.Text, nullable=False)
    author_id    = db.Column(db.Integer, db.ForeignKey('users.id'))

    # Priority: normal | high | urgent
    priority     = db.Column(db.String(20), default='normal')
    is_published = db.Column(db.Boolean, default=True)
    expires_at   = db.Column(db.DateTime, nullable=True)
    created_at   = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at   = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = db.relationship('User', back_populates='announcements')

    def to_dict(self):
        return {
            'id':           self.id,
            'title':        self.title,
            'content':      self.content,
            'author':       self.author.full_name if self.author else None,
            'priority':     self.priority,
            'is_published': self.is_published,
            'expires_at':   self.expires_at.isoformat() if self.expires_at else None,
            'created_at':   self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────
# NOTIFICATIONS
# ─────────────────────────────────────────────
class Notification(db.Model):
    __tablename__ = 'notifications'

    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title      = db.Column(db.String(200), nullable=False)
    message    = db.Column(db.Text)
    is_read    = db.Column(db.Boolean, default=False)
    link       = db.Column(db.String(300))                      # optional deep-link
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='notifications')

    def to_dict(self):
        return {
            'id':         self.id,
            'title':      self.title,
            'message':    self.message,
            'is_read':    self.is_read,
            'link':       self.link,
            'created_at': self.created_at.isoformat(),
        }


# ─────────────────────────────────────────────
# AUDIT LOG
# ─────────────────────────────────────────────
class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id          = db.Column(db.Integer, primary_key=True)
    user_id     = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    action      = db.Column(db.String(100), nullable=False)     # e.g. 'ticket.create'
    target_type = db.Column(db.String(50))                      # e.g. 'Ticket'
    target_id   = db.Column(db.Integer)                         # e.g. ticket ID
    details     = db.Column(db.Text)                            # JSON details
    ip_address  = db.Column(db.String(45))
    created_at  = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', back_populates='audit_logs')

    def to_dict(self):
        return {
            'id':          self.id,
            'user':        self.user.full_name if self.user else 'System',
            'action':      self.action,
            'target_type': self.target_type,
            'target_id':   self.target_id,
            'details':     self.details,
            'ip_address':  self.ip_address,
            'created_at':  self.created_at.isoformat(),
        }