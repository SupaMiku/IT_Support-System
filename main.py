"""
School IT Support System
Flask Application Entry Point
"""

import os
from flask import Flask, render_template, redirect, url_for, session
from database import db
from routes.auth      import auth_bp
from routes.tickets   import tickets_bp
from routes.assets    import assets_bp
from routes.users     import users_bp
from routes.kb        import kb_bp
from routes.announcements import announce_bp
from routes.dashboard import dashboard_bp

def create_app():
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    
    app = Flask(
        __name__,
        template_folder=os.path.join(BASE_DIR, 'templates'),
        static_folder=os.path.join(BASE_DIR, 'static'),
        static_url_path='/static'
    )

    # ── Configuration ──────────────────────────────────────────────
    app.config['SECRET_KEY']          = 'school-it-secret-key-change-in-prod'
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(BASE_DIR, 'it_support.db')
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # ── Initialize extensions ──────────────────────────────────────
    db.init_app(app)

    # ── Register blueprints ────────────────────────────────────────
    app.register_blueprint(auth_bp,      url_prefix='/api/auth')
    app.register_blueprint(tickets_bp,   url_prefix='/api/tickets')
    app.register_blueprint(assets_bp,    url_prefix='/api/assets')
    app.register_blueprint(users_bp,     url_prefix='/api/users')
    app.register_blueprint(kb_bp,        url_prefix='/api/kb')
    app.register_blueprint(announce_bp,  url_prefix='/api/announcements')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')

    # ── Page Routes ────────────────────────────────────────────────
    @app.route('/')
    def index():
        """Redirect home to login"""
        return redirect(url_for('login'))

    @app.route('/login')
    def login():
        """Login page"""
        return render_template('login.html')

    @app.route('/register')
    def register():
        """Register page"""
        return render_template('register.html')

    @app.route('/dashboard')
    def dashboard():
        """Dashboard page"""
        # Check if user is logged in
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return render_template('dashboard.html')

    @app.route('/logout')
    def logout():
        """Logout user"""
        session.clear()
        return redirect(url_for('login'))

    # ── Create tables & seed data on first run ─────────────────────
    with app.app_context():
        db.create_all()
        seed_data()

    return app


def seed_data():
    """Insert sample data only if the DB is empty."""
    from models import User, Role
    if User.query.first():
        return  # already seeded

    from werkzeug.security import generate_password_hash
    from datetime import datetime, date

    # Roles
    admin_role   = Role(name='admin',   description='Full system access')
    staff_role   = Role(name='it_staff',description='IT staff – manage tickets & assets')
    faculty_role = Role(name='faculty', description='Faculty – submit & view own tickets')
    student_role = Role(name='student', description='Student – submit tickets only')
    db.session.add_all([admin_role, staff_role, faculty_role, student_role])
    db.session.flush()

    # Users
    from models import User
    admin = User(
        username='admin',
        email='admin@school.edu',
        password_hash=generate_password_hash('Admin@1234'),
        full_name='IT Administrator',
        role_id=admin_role.id,
        department='IT Department',
        is_active=True
    )
    staff = User(
        username='itstaff',
        email='staff@school.edu',
        password_hash=generate_password_hash('Staff@1234'),
        full_name='IT Staff Member',
        role_id=staff_role.id,
        department='IT Department',
        is_active=True
    )
    teacher = User(
        username='mssantos',
        email='santos@school.edu',
        password_hash=generate_password_hash('Teacher@1234'),
        full_name='Ms. Santos',
        role_id=faculty_role.id,
        department='Science Department',
        is_active=True
    )
    student = User(
        username='juan2025',
        email='juan@school.edu',
        password_hash=generate_password_hash('Student@1234'),
        full_name='Juan Dela Cruz',
        role_id=student_role.id,
        department='Grade 11 - STEM',
        is_active=True
    )
    db.session.add_all([admin, staff, teacher, student])
    db.session.flush()

    # Tickets
    from models import Ticket, TicketComment
    t1 = Ticket(
        title='Projector not working – Room 204',
        description='The projector in Room 204 does not turn on. Tried all switches.',
        category='hardware',
        priority='high',
        status='open',
        requester_id=teacher.id,
        assigned_to_id=staff.id,
        location='Room 204'
    )
    t2 = Ticket(
        title='Cannot connect to school WiFi',
        description='My laptop keeps disconnecting from SchoolNet every few minutes.',
        category='network',
        priority='medium',
        status='in_progress',
        requester_id=student.id,
        assigned_to_id=staff.id,
        location='Library'
    )
    t3 = Ticket(
        title='Printer offline – Faculty Room',
        description='HP LaserJet in faculty room shows offline. Cannot print.',
        category='hardware',
        priority='high',
        status='open',
        requester_id=teacher.id,
        assigned_to_id=None,
        location='Faculty Room'
    )
    t4 = Ticket(
        title='PC won\'t boot – Lab 3, Unit 07',
        description='Computer unit 07 in Lab 3 shows black screen on startup.',
        category='hardware',
        priority='critical',
        status='in_progress',
        requester_id=staff.id,
        assigned_to_id=staff.id,
        location='Computer Lab 3'
    )
    t5 = Ticket(
        title='Email account locked',
        description='Student account locked after multiple failed logins.',
        category='account',
        priority='low',
        status='resolved',
        requester_id=student.id,
        assigned_to_id=admin.id,
        location='N/A',
        resolved_at=datetime.utcnow()
    )
    db.session.add_all([t1, t2, t3, t4, t5])
    db.session.flush()

    c1 = TicketComment(ticket_id=t1.id, author_id=staff.id,
                       content='Checked power supply – ordering replacement lamp unit.')
    c2 = TicketComment(ticket_id=t2.id, author_id=staff.id,
                       content='Updated WiFi driver and reset DHCP lease. Monitoring.')
    c3 = TicketComment(ticket_id=t5.id, author_id=admin.id,
                       content='Account unlocked and password reset sent to student email.')
    db.session.add_all([c1, c2, c3])

    # Assets
    from models import Asset, AssetMaintenance
    assets = [
        Asset(asset_tag='PC-LAB1-01', name='Desktop PC',    category='computer',  brand='Acer',    model='Aspire TC',     serial_number='SN001', status='active',      location='Computer Lab 1', purchase_date=date(2022,6,1),  purchase_cost=25000.0, assigned_to_id=None),
        Asset(asset_tag='PC-LAB3-07', name='Desktop PC',    category='computer',  brand='Dell',    model='OptiPlex 3080', serial_number='SN007', status='maintenance', location='Computer Lab 3', purchase_date=date(2021,3,15), purchase_cost=28000.0, assigned_to_id=None),
        Asset(asset_tag='LPT-ADMIN-01',name='Laptop',       category='laptop',    brand='Lenovo',  model='ThinkPad E14',  serial_number='SN050', status='active',      location='Admin Office',   purchase_date=date(2023,1,10), purchase_cost=42000.0, assigned_to_id=admin.id),
        Asset(asset_tag='PRN-FAC-01', name='Laser Printer', category='printer',   brand='HP',      model='LaserJet M404', serial_number='SN101', status='inactive',    location='Faculty Room',   purchase_date=date(2020,8,20), purchase_cost=15000.0, assigned_to_id=None),
        Asset(asset_tag='PRJ-R204-01',name='Projector',     category='projector', brand='Epson',   model='EB-X41',        serial_number='SN201', status='maintenance', location='Room 204',       purchase_date=date(2021,5,10), purchase_cost=35000.0, assigned_to_id=None),
        Asset(asset_tag='AP-LIB-01',  name='Access Point',  category='network',   brand='Cisco',   model='Aironet 1815',  serial_number='SN301', status='active',      location='Library',        purchase_date=date(2022,9,5),  purchase_cost=12000.0, assigned_to_id=None),
        Asset(asset_tag='SWT-IT-01',  name='Network Switch',category='network',   brand='Cisco',   model='Catalyst 2960', serial_number='SN302', status='active',      location='IT Room',        purchase_date=date(2020,1,15), purchase_cost=18000.0, assigned_to_id=None),
        Asset(asset_tag='SRV-IT-01',  name='File Server',   category='server',    brand='HP',      model='ProLiant DL20', serial_number='SN401', status='active',      location='Server Room',    purchase_date=date(2021,11,1), purchase_cost=95000.0, assigned_to_id=None),
    ]
    db.session.add_all(assets)
    db.session.flush()

    maint = AssetMaintenance(
        asset_id=assets[1].id,
        performed_by_id=staff.id,
        maintenance_type='repair',
        description='Black screen on boot – checking RAM and HDD.',
        scheduled_date=date.today(),
        status='in_progress'
    )
    db.session.add(maint)

    # Knowledge Base
    from models import KnowledgeBaseArticle
    articles = [
        KnowledgeBaseArticle(
            title='How to Connect to SchoolNet WiFi',
            content='1. Click the WiFi icon on your taskbar.\n2. Select "SchoolNet" from the list.\n3. Enter your student/faculty credentials.\n4. Click Connect.',
            category='network',
            author_id=admin.id,
            is_published=True,
            views=145
        ),
        KnowledgeBaseArticle(
            title='Resetting Your School Email Password',
            content='Visit the self-service portal at portal.school.edu and click "Forgot Password". Enter your school email and follow the reset instructions sent to your recovery email.',
            category='account',
            author_id=admin.id,
            is_published=True,
            views=230
        ),
        KnowledgeBaseArticle(
            title='Troubleshooting a Printer Offline Error',
            content='1. Check that the printer is powered on.\n2. Go to Control Panel > Devices and Printers.\n3. Right-click the printer and select "See what\'s printing".\n4. Click Printer > Uncheck "Use Printer Offline".',
            category='hardware',
            author_id=staff.id,
            is_published=True,
            views=89
        ),
    ]
    db.session.add_all(articles)

    # Announcements
    from models import Announcement
    announcements = [
        Announcement(
            title='Scheduled Network Maintenance – March 5',
            content='The school network will undergo maintenance on March 5, 2025 from 8PM to 11PM. Internet access will be unavailable during this period.',
            author_id=admin.id,
            is_published=True,
            priority='high'
        ),
        Announcement(
            title='New IT Helpdesk Hours',
            content='Starting March 10, the IT helpdesk will be available from 7AM to 6PM Monday to Friday.',
            author_id=admin.id,
            is_published=True,
            priority='normal'
        ),
        Announcement(
            title='Software Update – All Lab Computers',
            content='All laboratory computers will be updated to Windows 11 during the summer break. Please save all personal files to your network drive before June 1.',
            author_id=staff.id,
            is_published=True,
            priority='normal'
        ),
    ]
    db.session.add_all(announcements)

    db.session.commit()
    print("✅  Database seeded successfully.")


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)