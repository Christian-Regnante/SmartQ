# SmartQ - Queue Management System

A modern queue management system designed for Rwanda to reduce waiting time at service points like hospitals and banks.

## 🚀 Features

- **Client Kiosk Interface**: Easy-to-use interface for clients to join queues
- **Staff Dashboard**: Real-time queue management for service providers
- **Admin Panel**: Complete system administration and analytics
- **SMS Notifications**: Automatic SMS confirmation for queue tickets
- **Real-time Updates**: Auto-refreshing dashboards for live queue status
- **Analytics**: Comprehensive reporting on service performance

## 📋 Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## 🛠️ Installation

### 1. Clone or Download the Project

Extract the SmartQ files to your desired location.

### 2. Set Up MySQL Database

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE smartq_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# Create user and grant privileges
CREATE USER 'smartq_user'@'localhost' IDENTIFIED BY 'smartq_password';
GRANT ALL PRIVILEGES ON smartq_db.* TO 'smartq_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Note**: If you want to use different credentials, update the `SQLALCHEMY_DATABASE_URI` in `config.py`.

### 3. Create Virtual Environment

```bash
# Navigate to project directory
cd smartq

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment (Optional)

Create a `.env` file in the project root for custom configuration:

```env
FLASK_CONFIG=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=mysql+pymysql://smartq_user:smartq_password@localhost/smartq_db
```

## 🚀 Running the Application

### Initialize and Start

```bash
python run.py
```

The application will:
1. Create all database tables
2. Initialize sample data (organizations, services, users)
3. Start the Flask development server on `http://localhost:5000`

### Default Credentials

**Admin Account:**
- Username: `admin`
- Password: `admin123`

**Staff Account:**
- Username: `nurse1`
- Password: `nurse123`

## 📱 Accessing the Application

Once running, visit:

- **Home**: http://localhost:5000
- **Client Kiosk**: http://localhost:5000/client
- **Staff Dashboard**: http://localhost:5000/staff/login
- **Admin Panel**: http://localhost:5000/admin/login

## 🏗️ Project Structure

```
smartq/
├── app/
│   ├── __init__.py           # Application factory
│   ├── models.py             # Database models
│   ├── routes/
│   │   ├── client.py         # Client kiosk routes
│   │   ├── staff.py          # Staff dashboard routes
│   │   ├── admin.py          # Admin panel routes
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css     # Stylesheet
│   │   ├── js/
│   │       ├── client.js     # Client interface logic
│   │       ├── dashboard.js  # Staff dashboard logic
│   │       └── admin.js      # Admin panel logic
│   ├── templates/
│       ├── client.html       # Client kiosk template
│       ├── staff_login.html  # Staff login page
│       ├── dashboard.html    # Staff dashboard
│       ├── admin_login.html  # Admin login page
│       └── admin.html        # Admin panel
├── config.py                 # Configuration settings
├── run.py                    # Application entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔑 Key Components

### Database Models

- **Organization**: Hospitals, banks, etc.
- **Service**: Services offered by organizations
- **User**: Admin and staff user accounts
- **ServiceProvider**: Staff members assigned to services
- **QueueItem**: Individual queue tickets
- **Analytics**: Daily performance metrics

### API Endpoints

#### Client Routes (`/client/api/`)
- `GET /organizations` - List all organizations
- `GET /services/<org_id>` - Get services for organization
- `POST /join-queue` - Join a service queue
- `GET /queue-status/<queue_number>` - Check ticket status
- `GET /now-serving/<service_id>` - Get currently serving ticket

#### Staff Routes (`/staff/api/`)
- `GET /my-service` - Get assigned service info
- `GET /queue` - Get current queue
- `POST /call-next` - Call next client
- `POST /complete/<item_id>` - Mark service complete
- `POST /skip/<item_id>` - Skip a client
- `GET /stats` - Get dashboard statistics

#### Admin Routes (`/admin/api/`)
- Organizations: `GET, POST, PUT, DELETE /organizations`
- Services: `GET, POST, PUT, DELETE /services`
- Providers: `GET, POST, PUT, DELETE /providers`
- Analytics: `GET /analytics/overview`, `GET /analytics/services`

## 🎨 User Interface

### Client Kiosk
- Clean, minimalist design with large touch-friendly buttons
- Step-by-step process: Select organization → Select service → Enter phone → Get ticket
- Displays queue position and estimated wait time
- SMS confirmation sent automatically

### Staff Dashboard
- Real-time queue display with auto-refresh (10s intervals)
- Currently serving client highlighted
- One-click actions: Call Next, Complete, Skip
- Statistics: Served today, Average service time, Queue length

### Admin Panel
- Tabbed interface for different management sections
- CRUD operations for organizations, services, and staff
- System-wide analytics and reporting
- Service performance metrics

## 🔧 Configuration

### Database Settings
Edit `config.py` to change database connection:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://user:password@host/database'
```

### SMS Integration
Currently using mock SMS. To integrate Twilio:

1. Sign up at https://www.twilio.com
2. Get your Account SID, Auth Token, and Phone Number
3. Update `config.py`:
```python
TWILIO_ACCOUNT_SID = 'your_account_sid'
TWILIO_AUTH_TOKEN = 'your_auth_token'
TWILIO_PHONE_NUMBER = '+250XXXXXXXXX'
```
4. Uncomment Twilio code in `app/routes/client.py`

## 🚦 Performance Optimizations

- **Database Indexing**: Optimized queries with indexes on frequently accessed columns
- **Connection Pooling**: SQLAlchemy connection pool for efficient database access
- **Async Operations**: Ready for async routes where needed
- **AJAX Requests**: No page reloads for smooth user experience
- **Auto-refresh**: Intelligent polling for real-time updates

## 🔐 Security Features

- Password hashing using Werkzeug
- CSRF protection with Flask-WTF
- Session management with secure cookies
- Role-based access control (Admin/Staff)
- SQL injection prevention via SQLAlchemy ORM

## 📊 Analytics

The system tracks:
- Total tickets issued
- Completion rates
- Average wait times
- Service performance per location
- Peak hours and queue lengths

## 🐛 Troubleshooting

### Database Connection Error
```bash
# Check MySQL is running
mysql -u root -p

# Verify database exists
SHOW DATABASES;

# Check user permissions
SHOW GRANTS FOR 'smartq_user'@'localhost';
```

### Port Already in Use
```bash
# Change port in run.py or set environment variable
export PORT=8000
python run.py
```

### Missing Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 🚀 Deployment

### Production Checklist

1. **Update Configuration**:
   - Set `FLASK_CONFIG=production`
   - Use strong `SECRET_KEY`
   - Enable HTTPS

2. **Database**:
   - Use production MySQL server
   - Enable SSL connection
   - Regular backups

3. **Web Server**:
   - Deploy with Gunicorn or uWSGI
   - Use Nginx as reverse proxy
   - Enable HTTPS with Let's Encrypt

4. **SMS Integration**:
   - Configure real Twilio credentials
   - Test SMS delivery

### Example Gunicorn Deployment

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## 🔄 Future Enhancements

- Mobile app for clients to check queue status
- WhatsApp notifications integration
- Multi-language support (Kinyarwanda, French, English)
- QR code tickets
- Appointment scheduling
- Video call integration for remote consultations
- Advanced analytics dashboard with charts
- Integration with hospital management systems

## 📝 License

This is an MVP (Minimum Viable Product) for demonstration and development purposes.

## 👥 Support

For issues or questions:
1. Check the troubleshooting section
2. Review the code comments
3. Test with the default sample data

## 🎯 Testing the System

### Test Workflow

1. **Admin Setup** (http://localhost:5000/admin/login):
   - Login with admin/admin123
   - Add new organization (e.g., "Bank of Kigali")
   - Add services (e.g., "Account Opening", "Loans")
   - Add staff members and assign to services

2. **Client Experience** (http://localhost:5000/client):
   - Select organization
   - Choose service
   - Enter phone number (+250788XXXXXX)
   - Get queue ticket

3. **Staff Operations** (http://localhost:5000/staff/login):
   - Login with nurse1/nurse123
   - View waiting queue
   - Call next client
   - Complete service
   - Monitor statistics

## 📞 Contact

For Rwanda-specific deployment assistance or customization, consider the local tech community and development forums.

---

**Built with ❤️ for Rwanda's Digital Transformation**