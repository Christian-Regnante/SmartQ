# SmartQ - Complete Setup Guide

## 🎯 Quick Start (5 Minutes)

Follow these steps to get SmartQ running on your local machine.

### Step 1: Install MySQL

#### Windows:
1. Download MySQL Installer from https://dev.mysql.com/downloads/installer/
2. Run the installer and choose "Developer Default"
3. Set root password when prompted (remember this!)
4. Complete the installation

#### macOS:
```bash
brew install mysql
brew services start mysql
mysql_secure_installation
```

#### Linux (Ubuntu/Debian):
```bash
sudo apt update
sudo apt install mysql-server
sudo mysql_secure_installation
```

### Step 2: Set Up Database

Open MySQL command line:
```bash
mysql -u root -p
```

Run these commands:
```sql
CREATE DATABASE smartq_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'smartq_user'@'localhost' IDENTIFIED BY 'smartq_password';
GRANT ALL PRIVILEGES ON smartq_db.* TO 'smartq_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 3: Install Python Dependencies

#### Windows:
```cmd
cd smartq
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

#### macOS/Linux:
```bash
cd smartq
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Step 4: Run the Application

```bash
python run.py
```

You should see:
```
✅ Database initialized with sample data
👤 Admin: admin / admin123
👨‍⚕️ Staff: nurse1 / nurse123
 * Running on http://127.0.0.1:5000
```

### Step 5: Access the Application

Open your browser and visit:
- **Home**: http://localhost:5000
- **Client Kiosk**: http://localhost:5000/client
- **Staff Dashboard**: http://localhost:5000/staff/login (nurse1/nurse123)
- **Admin Panel**: http://localhost:5000/admin/login (admin/admin123)

---

## 🔧 Detailed Setup Instructions

### Prerequisites Checklist

- [ ] Python 3.8 or higher installed
- [ ] MySQL 5.7 or higher installed and running
- [ ] pip package manager available
- [ ] Git (optional, for cloning)

### Verify Installations

```bash
# Check Python version
python --version  # Should be 3.8+

# Check pip
pip --version

# Check MySQL
mysql --version
```

### Project Structure Setup

Create the following directory structure:

```
smartq/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes/
│   │   ├── __init__.py (create empty file)
│   │   ├── client.py
│   │   ├── staff.py
│   │   └── admin.py
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── client.js
│   │       ├── dashboard.js
│   │       └── admin.js
│   └── templates/
│       ├── client.html
│       ├── staff_login.html
│       ├── dashboard.html
│       ├── admin_login.html
│       ├── admin.html
│       └── display.html
├── config.py
├── run.py
├── requirements.txt
└── README.md
```

**Important**: Create an empty `__init__.py` file in the `routes` directory:
```bash
# Windows
type nul > app/routes/__init__.py

# macOS/Linux
touch app/routes/__init__.py
```

### Database Configuration Options

#### Option 1: Use Default Settings (Recommended for Testing)
The default settings in `config.py` will work if you followed Step 2.

#### Option 2: Custom Database Settings
Edit `config.py` and update:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://your_user:your_password@your_host/your_database'
```

#### Option 3: Using Environment Variables
Create a `.env` file:

```env
DATABASE_URL=mysql+pymysql://smartq_user:smartq_password@localhost/smartq_db
SECRET_KEY=your-secret-key-here
FLASK_CONFIG=development
```

### Common Installation Issues

#### Issue 1: MySQL Connection Error
```
Error: Can't connect to MySQL server
```

**Solution**:
```bash
# Check if MySQL is running
# Windows:
net start MySQL80

# macOS:
brew services start mysql

# Linux:
sudo systemctl start mysql
```

#### Issue 2: Permission Denied
```
Error: Access denied for user 'smartq_user'@'localhost'
```

**Solution**: Re-run the GRANT command in MySQL:
```sql
GRANT ALL PRIVILEGES ON smartq_db.* TO 'smartq_user'@'localhost';
FLUSH PRIVILEGES;
```

#### Issue 3: Module Not Found
```
ModuleNotFoundError: No module named 'flask'
```

**Solution**: Make sure virtual environment is activated:
```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

# Then reinstall
pip install -r requirements.txt
```

#### Issue 4: Port Already in Use
```
Error: Address already in use
```

**Solution**: Change port in run.py or:
```bash
# Set different port
export PORT=8000
python run.py
```

#### Issue 5: PyMySQL Installation Issues
```
Error installing PyMySQL
```

**Solution**:
```bash
pip install --upgrade pip
pip install PyMySQL --no-cache-dir
```

### Verification Tests

After installation, run these tests:

#### 1. Database Connection Test
```bash
python -c "from app import create_app; app = create_app(); print('Database connected!')"
```

#### 2. Create Test Ticket
1. Go to http://localhost:5000/client
2. Select "King Faisal Hospital"
3. Select "General Consultation"
4. Enter phone: +250788123456
5. Verify ticket is created

#### 3. Staff Dashboard Test
1. Go to http://localhost:5000/staff/login
2. Login with nurse1/nurse123
3. Verify you can see the queue
4. Click "Call Next"
5. Complete the service

#### 4. Admin Panel Test
1. Go to http://localhost:5000/admin/login
2. Login with admin/admin123
3. Navigate to Organizations tab
4. Try adding a new organization
5. Check analytics in Overview tab

---

## 🚀 Production Deployment

### Preparation

1. **Update Configuration**:
```python
# config.py
class ProductionConfig(Config):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    SECRET_KEY = os.environ.get('SECRET_KEY')  # Use strong key
```

2. **Use Production Database**:
```env
DATABASE_URL=mysql+pymysql://user:pass@production-host/db
```

3. **Install Gunicorn**:
```bash
pip install gunicorn
```

### Deployment Options

#### Option 1: Simple Production Server
```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

#### Option 2: With Nginx (Recommended)

1. Install Nginx:
```bash
sudo apt install nginx
```

2. Create Nginx config (`/etc/nginx/sites-available/smartq`):
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /static {
        alias /path/to/smartq/app/static;
    }
}
```

3. Enable site:
```bash
sudo ln -s /etc/nginx/sites-available/smartq /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### Option 3: Docker Deployment

Create `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "run:app"]
```

Create `docker-compose.yml`:
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=mysql+pymysql://user:pass@db/smartq_db
    depends_on:
      - db

  db:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=rootpass
      - MYSQL_DATABASE=smartq_db
      - MYSQL_USER=smartq_user
      - MYSQL_PASSWORD=smartq_password
    volumes:
      - mysql_data:/var/lib/mysql

volumes:
  mysql_data:
```

Run:
```bash
docker-compose up -d
```

---

## 🔐 Security Hardening

### 1. Change Default Passwords
```sql
UPDATE users SET password_hash = '<new_hash>' WHERE username = 'admin';
```

Or use the admin panel to update passwords.

### 2. Enable HTTPS
Use Let's Encrypt with Certbot:
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

### 3. Configure Firewall
```bash
sudo ufw allow 80
sudo ufw allow 443
sudo ufw enable
```

### 4. Secure MySQL
```bash
mysql_secure_installation
```

### 5. Use Strong Secret Key
```python
import secrets
print(secrets.token_hex(32))
```

Use this in your `.env` file.

---

## 📊 Monitoring and Maintenance

### Daily Checks
- Verify application is running: `curl http://localhost:5000`
- Check database connection
- Review error logs

### Weekly Tasks
- Database backup:
```bash
mysqldump -u smartq_user -p smartq_db > backup_$(date +%Y%m%d).sql
```
- Review analytics
- Update staff schedules

### Monthly Tasks
- Update dependencies: `pip list --outdated`
- Security audit
- Performance optimization

### Backup Strategy

```bash
# Automated daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
mysqldump -u smartq_user -p smartq_db > /backups/smartq_$DATE.sql
find /backups -name "smartq_*.sql" -mtime +7 -delete
```

---

## 🆘 Emergency Procedures

### Application Not Starting
1. Check if MySQL is running
2. Verify database credentials
3. Check for port conflicts
4. Review error logs

### Database Connection Lost
1. Restart MySQL: `sudo systemctl restart mysql`
2. Check user permissions
3. Verify network connectivity

### High Queue Times
1. Add more service providers
2. Increase service counters
3. Optimize service time estimates
4. Review analytics for bottlenecks

### Data Recovery
```bash
# Restore from backup
mysql -u smartq_user -p smartq_db < backup_file.sql
```

---

## 📞 Support Resources

### Useful Commands

```bash
# Check app status
ps aux | grep python

# View logs
tail -f /var/log/smartq/error.log

# Restart application
pkill -f "python run.py"
python run.py &

# Database status
systemctl status mysql
```

### Testing Endpoints

```bash
# Test API endpoints
curl http://localhost:5000/client/api/organizations
curl http://localhost:5000/client/api/services/1
```

### Performance Tuning

1. **Database Optimization**:
```sql
ANALYZE TABLE queue_items;
OPTIMIZE TABLE queue_items;
```

2. **Application Caching**: Consider Redis for session storage

3. **Load Balancing**: Use multiple Gunicorn workers

---

## ✅ Post-Installation Checklist

- [ ] MySQL installed and running
- [ ] Database and user created
- [ ] Virtual environment created and activated
- [ ] Dependencies installed
- [ ] Application starts without errors
- [ ] Can access all three interfaces (client, staff, admin)
- [ ] Can create a test ticket
- [ ] Can process queue from staff dashboard
- [ ] Can manage system from admin panel
- [ ] Database backup configured
- [ ] Security settings reviewed
- [ ] Documentation read and understood

---

## 🎓 Training Materials

### For Administrators
1. System overview and architecture
2. Adding organizations and services
3. Managing staff accounts
4. Reading analytics
5. Troubleshooting common issues

### For Staff
1. Logging in to dashboard
2. Managing queue
3. Calling next client
4. Completing services
5. Handling no-shows

### For Clients
1. Using the kiosk
2. Understanding queue tickets
3. SMS notifications
4. Estimated wait times

---

## 📈 Next Steps

After successful installation:

1. **Customize for Your Organization**
   - Add your organizations
   - Configure services
   - Set up staff accounts
   - Adjust service time estimates

2. **Integrate SMS Service**
   - Sign up for Twilio
   - Configure credentials
   - Test notifications

3. **Deploy Display Screens**
   - Set up tablets/screens at counters
   - Access display URL with service parameter
   - Example: `http://localhost:5000/client/display?service=1`

4. **Train Your Team**
   - Run training sessions for staff
   - Create user guides
   - Establish support procedures

5. **Monitor and Optimize**
   - Review analytics regularly
   - Gather user feedback
   - Adjust configurations as needed

---

**Need Help?** Review the README.md for detailed feature documentation and API references.