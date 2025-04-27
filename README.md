# ESI Document Backend

A modern document management system for ESI (École Nationale Supérieure d'Informatique) built with Django REST Framework. This system manages administrative documents, employee data, attestations, mission orders, and provides a comprehensive dashboard for analytics.

## Features

- **Authentication System**

  - JWT-based authentication
  - Role-based access control (Admin, HR, Secretary General)
  - Password reset functionality
  - Secure token management

- **User Management**

  - User registration with role assignment
  - Automated temporary password generation and email notifications
  - Profile management

- **Document Management**

  - Employee records management
  - Work certificates (attestations) generation
  - Mission orders with multi-stage journey support
  - Automated reference numbering

- **Dashboard & Analytics**

  - Real-time statistics on users, employees, and documents
  - Activity monitoring
  - Customizable dashboard preferences

- **Notification System**

  - In-app notifications
  - Email notifications for important events
  - Read/unread status tracking

- **Activity Logging**
  - Comprehensive audit trail
  - User action tracking
  - IP and user agent logging

## Technology Stack

- **Backend:** Django 5.0+, Django REST Framework
- **Database:** PostgreSQL
- **Authentication:** JWT (djangorestframework-simplejwt)
- **Documentation:** drf-spectacular (OpenAPI)
- **Static Files:** WhiteNoise
- **Server:** Gunicorn
- **Email:** SMTP integration

## Installation

### Prerequisites

- Python 3.9+
- PostgreSQL

### Setup

1. **Clone the repository**

   ```
   git clone <repository-url>
   cd ESI_document_backend
   ```

2. **Create a virtual environment**

   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   ```
   pip install -r requirements.txt
   ```

4. **Configure environment variables**

   ```
   cp .env.example .env
   ```

   Edit `.env` with your specific configuration.

5. **Create database**

   ```
   # In PostgreSQL
   CREATE DATABASE esi_document_db;
   CREATE USER esi_document_user WITH PASSWORD 'your_password';
   GRANT ALL PRIVILEGES ON DATABASE esi_document_db TO esi_document_user;
   ```

6. **Apply migrations**

   ```
   python manage.py makemigrations
   python manage.py migrate
   ```

7. **Create a superuser**

   ```
   python manage.py createsuperuser
   ```

8. **Run the server**
   ```
   python manage.py runserver
   ```

## API Documentation

The API documentation is available through Swagger UI and ReDoc:

- Swagger UI: `/api/schema/swagger/`
- ReDoc: `/api/schema/redoc/`
- Download OpenAPI schema: `/api/schema/`

### API Endpoints

The API is organized into several main sections:

- **Authentication**: `/api/accounts/login/`, `/api/accounts/logout/`, etc.
- **Users**: `/api/accounts/users/`
- **Notifications**: `/api/accounts/notifications/`
- **Employees**: `/api/documents/employees/`
- **Attestations**: `/api/documents/attestations/`
- **Mission Orders**: `/api/documents/missions/`
- **Dashboard**: `/api/dashboard/stats/`
- **Activities**: `/api/dashboard/activities/`

## Project Structure

```
ESI_document_backend/
├── ESI_document_project/     # Project settings
├── apps/                     # Application modules
│   ├── accounts/             # User authentication and management
│   ├── documents/            # Document generation and management
│   └── dashboard/            # Analytics and activity logging
├── media/                    # Media files (user uploads)
├── staticfiles/              # Collected static files (generated)
├── logs/                     # Application logs
├── manage.py                 # Django management script
├── requirements.txt          # Dependencies
├── build.sh                  # Render build script
├── Procfile                  # Process file for deployment
└── README.md                 # This file
```

## Role-Based Access

The system implements three roles with specific permissions:

1. **Admin**: Full access to all features, user management
2. **Human Resources (RH)**: Manage employees and documents
3. **Secretary General (SG)**: View and generate documents

## Development

### Coding Standards

- Follow PEP 8 style guide
- Use Black for code formatting
- Use Flake8 for linting

### Running Tests

```
python manage.py test
```

## Deployment

### Deployment to Render

1. Create a new Web Service on Render
2. Connect your GitHub repository
3. Select "Python" as the environment
4. Use the following settings:
   - Build Command: `./build.sh`
   - Start Command: `gunicorn ESI_document_project.wsgi:application`
5. Add the environment variables from your `.env` file
6. Deploy the application

### Manual Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure proper `ALLOWED_HOSTS`
3. Set up a proper database with secure credentials
4. Use Gunicorn as the WSGI server
5. Set up Nginx as a reverse proxy (optional)
6. Configure SSL certificates

Example Gunicorn command:

```
gunicorn ESI_document_project.wsgi:application --bind 0.0.0.0:8000
```

## Credits

Developed for ESI (École Nationale Supérieure d'Informatique)
