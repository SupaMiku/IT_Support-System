# School IT Support System - Setup Guide

## 📋 Requirements
- Python 3.8+
- Flask 2.3.3+
- Flask-SQLAlchemy 3.0.5+

## 🚀 Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Application
```bash
python main.py
```

The application will start on `http://localhost:5000`

## 📍 Available Pages

### Authentication
- **Login**: `http://localhost:5000/login`
- **Register**: `http://localhost:5000/register`
- **Dashboard**: `http://localhost:5000/dashboard`

## 👤 Test Credentials (Pre-seeded)

After first run, you can login with:

| Username | Email | Password | Role |
|----------|-------|----------|------|
| admin | admin@school.edu | Admin@1234 | Admin |
| itstaff | staff@school.edu | Staff@1234 | IT Staff |
| juan2025 | juan@school.edu | Student@1234 | Student |

## 🔧 Project Structure

```
IT_Support-System/
├── templates/              # HTML pages
│   ├── login.html
│   ├── register.html
│   └── dashboard.html
├── static/                 # Static assets
│   ├── css/               # Stylesheets
│   │   ├── login.css
│   │   ├── register.css
│   │   └── dashboard.css
│   └── auth.js            # Authentication handler
├── routes/                # API blueprints
│   ├── auth.py            # Login/Register endpoints
│   ├── tickets.py
│   ├── assets.py
│   ├── users.py
│   ├── kb.py
│   ├── announcements.py
│   └── dashboard.py
├── main.py                # Flask app entry point
├── models.py              # Database models
├── database.py            # SQLAlchemy instance
└── requirements.txt       # Python dependencies
```

## 📝 API Endpoints

### Authentication
- `POST /api/auth/register` - Create new account
- `POST /api/auth/login` - Login to account
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Get current user

### Tickets
- `GET /api/tickets/` - List all tickets
- `POST /api/tickets/` - Create ticket
- `GET /api/tickets/<id>` - Get ticket details

### Other Endpoints
- Assets: `/api/assets/`
- Users: `/api/users/`
- Knowledge Base: `/api/kb/`
- Announcements: `/api/announcements/`
- Dashboard: `/api/dashboard/summary`

## 🔒 Security Notes

- Change `SECRET_KEY` in production
- Implement HTTPS in production
- Add proper password hashing policies
- Implement rate limiting
- Add CORS configuration for cross-origin requests

## 🐛 Troubleshooting

### Database Issues
If you get database errors, delete `it_support.db` and restart the app to re-seed.

### Port Already in Use
Change the port in the `if __name__ == '__main__':` section at the bottom of `main.py`

### Static Files Not Loading
Ensure the `static/` folder exists with proper subdirectories (`css/`, etc.)
