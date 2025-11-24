# SmartQ - Queue Management System

A comprehensive queue management system designed for Rwanda to reduce waiting time at service points like hospitals and banks.

## Features

- **Multi-Organization Support**: Manage multiple organizations from a single platform
- **Role-Based Access Control**: Super Admin, Organization Admin, Staff roles
- **Real-Time Queue Management**: Live updates and status tracking
- **Unified Display System**: Single display page showing all services per organization
- **Analytics Dashboard**: Track performance metrics and wait times
- **SMS Notifications**: Mock SMS system (ready for Twilio integration)
- **Responsive Design**: Clean, minimalist GovTech-style interface

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: MySQL with SQLAlchemy ORM
- **Frontend**: HTML, CSS, JavaScript
- **Architecture**: REST API with async requests

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

### Installation

1. **Clone or download the project**

2. **Set up MySQL Database**

```bash
# Login to MySQL
mysql -u root -p

# Create database
CREATE DATABASE smartq_db;
exit;
```

3. **Install Python dependencies**

```bash
pip install -r requirements.txt
```

4. **Configure Database Connection**

Edit `config.py` and update the MySQL connection string:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:YOUR_PASSWORD@localhost/smartq_db'
```

Replace `YOUR_PASSWORD` with your MySQL root password.

5. **Initialize the Database**

```bash
python run.py
```

The application will automatically create all tables and a default super admin account.

## Running the Application

```bash
python run.py
```

The server will start on `http://localhost:5000`

## Default Login Credentials

### Super Admin
- **Username**: `superadmin`
- **Password**: `admin123`
- **URL**: http://localhost:5000/super-admin/login

## User Roles and Access

### Super Admin
- Full system access
- Manage organizations
- Create and assign organization admins
- View global analytics
- **Dashboard**: `/super-admin/dashboard`

### Organization Admin
- Manage services within their organization
- Add/edit/delete staff members
- View organization analytics
- **Dashboard**: `/admin/dashboard`

### Staff
- Manage queue for their assigned service
- Call next person in queue
- Mark clients as done or skipped
- View daily statistics
- **Dashboard**: `/staff/dashboard`

### Client (Public)
- Select organization and service
- Enter phone number
- Get queue ticket
- **Kiosk Interface**: `/client/`
- **Display Screen**: `/client/display?org_id=X`

## Usage Flow

1. **Super Admin Setup**
   - Login as super admin
   - Create organizations (e.g., "King Faisal Hospital", "Bank of Kigali")
   - Create organization admins and assign them to organizations

2. **Organization Admin Setup**
   - Login with admin credentials
   - Create services (e.g., "Consultation", "Pharmacy", "Withdrawal")
   - Add staff members and assign them to services

3. **Staff Operation**
   - Login with staff credentials
   - Use "Call Next" button to serve clients
   - Mark clients as done or skip when needed
   - Monitor daily statistics

4. **Client Experience**
   - Visit kiosk interface
   - Select organization and service
   - Enter phone number
   - Receive ticket with queue number and estimated wait time

5. **Display Screen**
   - Set up display screen at service point
   - Visit `/client/display?org_id=X` where X is the organization ID
   - Shows real-time "Now Serving" information for all services
   - Auto-refreshes every 3 seconds

## API Endpoints

### Client Routes
- `GET /client/` - Kiosk interface
- `GET /client/api/organizations` - List organizations
- `GET /client/api/services?org_id=X` - List services
- `POST /client/api/join-queue` - Join queue
- `GET /client/display?org_id=X` - Display screen
- `GET http://127.0.0.1:5001/client/display?org_id=1` - Example display screen URL`
- `GET /client/api/display-status?org_id=X` - Get display status

### Staff Routes
- `GET /staff/login` - Login page
- `GET /staff/dashboard` - Staff dashboard
- `GET /staff/api/queue` - Get queue items
- `POST /staff/api/call-next` - Call next client
- `POST /staff/api/mark-done/:id` - Mark client as done
- `POST /staff/api/skip/:id` - Skip client

### Admin Routes
- `GET /admin/login` - Login page
- `GET /admin/dashboard` - Admin dashboard
- `GET /admin/api/services` - List services
- `POST /admin/api/services` - Create service
- `PUT /admin/api/services/:id` - Update service
- `DELETE /admin/api/services/:id` - Delete service
- `GET /admin/api/staff` - List staff
- `POST /admin/api/staff` - Create staff
- `GET /admin/api/analytics` - Get analytics

### Super Admin Routes
- `GET /super-admin/login` - Login page
- `GET /super-admin/dashboard` - Super admin dashboard
- `GET /super-admin/api/organizations` - List organizations
- `POST /super-admin/api/organizations` - Create organization
- `PUT /super-admin/api/organizations/:id` - Update organization
- `DELETE /super-admin/api/organizations/:id` - Delete organization
- `GET /super-admin/api/admins` - List admins
- `POST /super-admin/api/admins` - Create admin
- `GET /super-admin/api/overview` - System overview

## Database Schema

### Organizations
- id, name, location, contact, created_at

### Users
- id, username, password_hash, role (super_admin/admin/staff)
- organization_id (for admins and staff)
- service_id (for staff)

### Services
- id, name, organization_id, counter_number
- avg_service_time, is_active, created_at

### Queue Items
- id, queue_number, service_id, phone_number
- status (waiting/serving/done/skipped)
- created_at, called_at, completed_at

## Project Structure

```
smartq/
├── app/
│   ├── __init__.py              # App initialization
│   ├── models.py                # Database models
│   ├── routes/
│   │   ├── client.py            # Client routes
│   │   ├── staff.py             # Staff routes
│   │   ├── admin.py             # Admin routes
│   │   └── super_admin.py       # Super admin routes
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css        # Main styles
│   │   │   ├── display.css      # Display screen styles
│   │   │   └── dashboard.css    # Dashboard styles
│   │   └── js/
│   │       ├── client.js        # Client interface logic
│   │       ├── staff.js         # Staff dashboard logic
│   │       ├── admin.js         # Admin dashboard logic
│   │       └── super_admin.js   # Super admin logic
│   └── templates/
│       ├── client.html
│       ├── client_display.html
│       ├── staff_login.html
│       ├── staff_dashboard.html
│       ├── admin_login.html
│       ├── admin_dashboard.html
│       ├── super_admin_login.html
│       └── super_admin_dashboard.html
├── config.py                    # Configuration
├── run.py                       # Application entry point
├── requirements.txt             # Dependencies
└── README.md                    # Documentation
```

## Customization

### SMS Integration
Replace the mock SMS function in `app/routes/client.py` with actual Twilio integration:

```python
from twilio.rest import Client

def send_sms(phone, message):
    client = Client(app.config['TWILIO_ACCOUNT_SID'], app.config['TWILIO_AUTH_TOKEN'])
    client.messages.create(
        to=phone,
        from_=app.config['TWILIO_PHONE_NUMBER'],
        body=message
    )
```

### Styling
- Edit `app/static/css/style.css` for main interface
- Edit `app/static/css/dashboard.css` for dashboards
- Edit `app/static/css/display.css` for display screens

## Troubleshooting

### Database Connection Error
- Verify MySQL is running
- Check database credentials in `config.py`
- Ensure database `smartq_db` exists

### Port Already in Use
Change the port in `run.py`:
```python
app.run(debug=True, port=5001)
```

### Session Issues
Clear browser cookies or use incognito mode

## Security Considerations

**For Production:**
1. Change the SECRET_KEY in config.py
2. Use environment variables for sensitive data
3. Enable HTTPS
4. Set secure session cookies
5. Implement rate limiting
6. Add CSRF protection for forms
7. Use strong passwords for all accounts

## Future Enhancements

- Mobile app for clients
- Email notifications
- Advanced analytics and reporting
- Multi-language support
- Appointment booking
- Payment integration
- Printer integration for physical tickets

## Deployment (Production Server Setup)

This section explains how SmartQ was deployed on an Ubuntu server using **Nginx**, **Gunicorn**, and **Certbot**, and how the domain `smartq.regnante.tech` was configured.

### 1. Run SmartQ on the Server

Upload the SmartQ project to the server, then create a Python virtual environment:

```bash
cd /var/www/
sudo mkdir smartq
sudo chown $USER:$USER smartq
cd smartq

python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt

python run.py # Test the application

# It should run on:
http://localhost:5000
```

## 2. Install and Configure Nginx

### Install Nginx

```bash
sudo apt update & sudo apt upgrade -y
sudo apt install nginx -y
```
### Configure Nginx
Edit the Nginx configuration file:

```bash
sudo nano /etc/nginx/sites-available/smartq
```
Add the following configuration:

```nginx
server {
    listen 80;
    #server_name add_your_domain_here.domain; # change this to your domain

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
Enable the site and reload Nginx:

```bash
sudo ln -s /etc/nginx/sites-available/smartq /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```
## 3. Docker Setup and Configuration
### Docker installation
Step1: Install prerequisites
```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release
```
Step2: Add Docker’s official GPG key
```bash
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
```
Step3: Set up the stable repository
```bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
```
Step4: Update apt and install Docker Engine
```bash
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
```
Step5: Enable Docker to start on boot
```bash
sudo systemctl enable --now docker
docker --version # Verify installation
```
After this the docker should be installed successfully and running on your server.

## 4. Setting up SmartQ application with Docker
```bash
cd /var/www/smartq
```
In the root directory of the project, you will find two files named `Dockerfile` and `docker-compose.yml`. Use these files to build and run the Docker container for SmartQ.

### Build and run containers
```bash
sudo docker-compose up -d --build
sudo docker ps # Then check if the container is running you should see 2 contianers: smartq_web and smartq_db
```
### After running the containers, Test the application if it's running properly.
```bash
curl http://localhost:5000 # use curl to test if the application is running

sudo apt install -y curl # if curl is not installed
```

## 5. configure Nginx as a reverse proxy
### As the Nginx is already installed in step 2, Now:
1. We enable the Nginx site configuration for SmartQ.
```bash
sudo ln -s /etc/nginx/sites-available/smartq /etc/nginx/sites-enabled/
```
2. Test Nginx configuration and reload Nginx.
```bash
Sudo nginx -t
sudo systemctl reload nginx
```

Now your SmartQ application should be accessible via your server's IP address `http://your_server_ip`

## Support

For issues or questions, please contact the development team or create an issue in the repository.

© 2024 SmartQ. All rights reserved.