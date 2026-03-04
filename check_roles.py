from main import create_app
from database import db

app = create_app()
with app.app_context():
    from models import Role, User
    print("=== Database Roles ===")
    roles = Role.query.all()
    for role in roles:
        print(f"ID: {role.id}, Name: '{role.name}'")
    
    print("\n=== Recent Users (Last 10) ===")
    users = User.query.order_by(User.id.desc()).limit(10).all()
    if not users:
        print("No users found")
    else:
        for user in users:
            role_name = user.role.name if user.role else 'NONE'
            print(f"{user.id}: {user.email} -> Role ID {user.role_id} ({role_name})")
