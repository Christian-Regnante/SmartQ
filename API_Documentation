# SmartQ API Documentation
## RESTful API Reference Guide

**Version**: 1.0.0  
**Base URL**: `http://localhost:5000`  
**Protocol**: HTTP/HTTPS  
**Format**: JSON

---

## 📚 TABLE OF CONTENTS

1. [Authentication](#authentication)
2. [Client Kiosk APIs](#client-kiosk-apis)
3. [Staff Dashboard APIs](#staff-dashboard-apis)
4. [Admin Panel APIs](#admin-panel-apis)
5. [Super Admin APIs](#super-admin-apis)
6. [Error Responses](#error-responses)
7. [Status Codes](#status-codes)

---

## 🔐 AUTHENTICATION

### Authentication Methods

SmartQ uses **session-based authentication** with Flask-Login.

**Login Flow**:
1. Send POST request to login endpoint with credentials
2. Server validates and creates session
3. Session cookie automatically included in subsequent requests
4. Use session cookie for all authenticated endpoints

**Session Details**:
- **Session Duration**: 8 hours
- **Cookie Name**: `session`
- **Cookie Flags**: `HttpOnly`, `SameSite=Lax`
- **Storage**: Server-side session storage

---

## 🏪 CLIENT KIOSK APIs

These endpoints are **publicly accessible** (no authentication required).

---

### 1. Get All Organizations

Retrieve list of all active organizations.

**Endpoint**: `GET /client/api/organizations`

**Authentication**: None required

**Request**:
```http
GET /client/api/organizations HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "King Faisal Hospital",
    "type": "hospital",
    "location": "Kigali"
  },
  {
    "id": 2,
    "name": "Bank of Kigali",
    "type": "bank",
    "location": "Kigali City"
  }
]
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Organization unique identifier |
| name | string | Organization name |
| type | string | Type (hospital, bank, government, other) |
| location | string | Physical location |

**Status Codes**:
- `200 OK` - Success

---

### 2. Get Services for Organization

Retrieve all active services for a specific organization with current queue information.

**Endpoint**: `GET /client/api/services/:org_id`

**Authentication**: None required

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | integer | Yes | Organization ID |

**Request**:
```http
GET /client/api/services/1 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "General Consultation",
    "counter": "Room 101",
    "queue_length": 5,
    "estimated_wait": 75
  },
  {
    "id": 2,
    "name": "Pharmacy",
    "counter": "Counter 1",
    "queue_length": 2,
    "estimated_wait": 20
  }
]
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Service unique identifier |
| name | string | Service name |
| counter | string | Counter/Room number |
| queue_length | integer | Current number of people waiting |
| estimated_wait | integer | Estimated wait time in minutes |

**Status Codes**:
- `200 OK` - Success
- `404 Not Found` - Organization not found

---

### 3. Join Queue (Create Ticket)

Create a new queue ticket for a client.

**Endpoint**: `POST /client/api/join-queue`

**Authentication**: None required

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "service_id": 1,
  "phone": "+250788123456"
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| service_id | integer | Yes | Service ID to join |
| phone | string | Yes | Client phone number (format: +250XXXXXXXXX) |

**Request**:
```http
POST /client/api/join-queue HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "service_id": 1,
  "phone": "+250788123456"
}
```

**Response**:
```json
{
  "success": true,
  "queue_number": "Q202411011234",
  "position": 4,
  "estimated_wait": 45,
  "service_name": "General Consultation",
  "counter": "Room 101"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Operation success status |
| queue_number | string | Generated ticket number |
| position | integer | Current position in queue |
| estimated_wait | integer | Estimated wait time (minutes) |
| service_name | string | Name of service |
| counter | string | Counter/Room to go to |

**Validation Rules**:
- Phone must start with `+250`
- Phone must be exactly 13 characters
- Service must exist and be active

**Status Codes**:
- `200 OK` - Ticket created successfully
- `400 Bad Request` - Invalid input (missing fields, invalid phone)
- `404 Not Found` - Service not found

**Error Response**:
```json
{
  "error": "Invalid phone number. Use format: +250XXXXXXXXX"
}
```

---

### 4. Get Queue Status

Check the status of a specific queue ticket.

**Endpoint**: `GET /client/api/queue-status/:queue_number`

**Authentication**: None required

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| queue_number | string | Yes | Ticket number (e.g., Q202411011234) |

**Request**:
```http
GET /client/api/queue-status/Q202411011234 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

**Response**:
```json
{
  "queue_number": "Q202411011234",
  "status": "waiting",
  "position": 3,
  "service_name": "General Consultation",
  "counter": "Room 101",
  "created_at": "2024-11-01T10:30:00"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| queue_number | string | Ticket number |
| status | string | Current status (waiting, serving, completed, skipped) |
| position | integer | Current position (0 if not waiting) |
| service_name | string | Service name |
| counter | string | Counter/Room number |
| created_at | string | ISO 8601 timestamp |

**Status Codes**:
- `200 OK` - Success
- `404 Not Found` - Ticket not found

---

### 5. Get Now Serving (Single Service)

Get currently serving ticket for a specific service.

**Endpoint**: `GET /client/api/now-serving/:service_id`

**Authentication**: None required

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | integer | Yes | Service ID |

**Request**:
```http
GET /client/api/now-serving/1 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

**Response**:
```json
{
  "service_name": "General Consultation",
  "counter": "Room 101",
  "now_serving": "Q202411011234",
  "waiting_count": 5
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| service_name | string | Service name |
| counter | string | Counter/Room number |
| now_serving | string/null | Currently serving ticket number (null if none) |
| waiting_count | integer | Number of people waiting |

**Status Codes**:
- `200 OK` - Success
- `404 Not Found` - Service not found

---

### 6. Get Organization Display Data

Get all services and their current status for an organization (for unified display screen).

**Endpoint**: `GET /client/api/organization-display/:org_id`

**Authentication**: None required

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| org_id | integer | Yes | Organization ID |

**Request**:
```http
GET /client/api/organization-display/1 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
```

**Response**:
```json
{
  "organization_id": 1,
  "organization_name": "King Faisal Hospital",
  "services": [
    {
      "service_id": 1,
      "service_name": "General Consultation",
      "counter": "Room 101",
      "now_serving": "Q202411011234",
      "waiting_count": 5
    },
    {
      "service_id": 2,
      "service_name": "Pharmacy",
      "counter": "Counter 1",
      "now_serving": null,
      "waiting_count": 2
    }
  ]
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| organization_id | integer | Organization ID |
| organization_name | string | Organization name |
| services | array | Array of service objects |
| services[].service_id | integer | Service ID |
| services[].service_name | string | Service name |
| services[].counter | string | Counter/Room number |
| services[].now_serving | string/null | Currently serving ticket (null if none) |
| services[].waiting_count | integer | Number waiting |

**Status Codes**:
- `200 OK` - Success
- `404 Not Found` - Organization not found

---

## 👨‍💼 STAFF DASHBOARD APIs

These endpoints require **staff authentication**.

---

### 1. Staff Login

Authenticate staff member and create session.

**Endpoint**: `POST /staff/login`

**Authentication**: None required for this endpoint

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "username": "nurse1",
  "password": "nurse123"
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Staff username |
| password | string | Yes | Staff password |

**Request**:
```http
POST /staff/login HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "username": "nurse1",
  "password": "nurse123"
}
```

**Response**:
```json
{
  "success": true,
  "redirect": "/staff/dashboard"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Login success status |
| redirect | string | URL to redirect to |

**Status Codes**:
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials

**Error Response**:
```json
{
  "error": "Invalid credentials"
}
```

**Notes**:
- Session cookie automatically set on success
- Session expires after 8 hours of inactivity

---

### 2. Get My Service

Get information about the staff member's assigned service.

**Endpoint**: `GET /staff/api/my-service`

**Authentication**: Required (Staff)

**Request**:
```http
GET /staff/api/my-service HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
{
  "service_id": 1,
  "service_name": "General Consultation",
  "counter": "Room 101",
  "provider_name": "Dr. Jane Mugisha"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| service_id | integer | Service ID |
| service_name | string | Service name |
| counter | string | Counter/Room number |
| provider_name | string | Staff member's full name |

**Status Codes**:
- `200 OK` - Success
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not a staff member
- `404 Not Found` - Service provider profile not found

---

### 3. Get Queue

Get current queue for staff member's service.

**Endpoint**: `GET /staff/api/queue`

**Authentication**: Required (Staff)

**Request**:
```http
GET /staff/api/queue HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
{
  "waiting": [
    {
      "id": 45,
      "queue_number": "Q202411011234",
      "phone": "3456",
      "created_at": "14:20",
      "position": 1
    },
    {
      "id": 46,
      "queue_number": "Q202411011235",
      "phone": "4567",
      "created_at": "14:22",
      "position": 2
    }
  ],
  "serving": {
    "id": 44,
    "queue_number": "Q202411011233",
    "phone": "2345",
    "serving_since": "14:15"
  }
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| waiting | array | Array of waiting queue items |
| waiting[].id | integer | Queue item ID |
| waiting[].queue_number | string | Ticket number |
| waiting[].phone | string | Last 4 digits of phone (privacy) |
| waiting[].created_at | string | Time joined (HH:MM format) |
| waiting[].position | integer | Position in queue |
| serving | object/null | Currently serving item (null if none) |
| serving.id | integer | Queue item ID |
| serving.queue_number | string | Ticket number |
| serving.phone | string | Last 4 digits |
| serving.serving_since | string | Time started serving (HH:MM) |

**Status Codes**:
- `200 OK` - Success
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not a staff member
- `404 Not Found` - Service provider profile not found

---

### 4. Call Next Client

Call the next client in the queue.

**Endpoint**: `POST /staff/api/call-next`

**Authentication**: Required (Staff)

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**: None

**Request**:
```http
POST /staff/api/call-next HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
{
  "success": true,
  "queue_number": "Q202411011234",
  "phone": "3456"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Operation success |
| queue_number | string | Ticket number called |
| phone | string | Last 4 digits of phone |

**Status Codes**:
- `200 OK` - Client called successfully
- `400 Bad Request` - Already serving someone or no clients in queue
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not a staff member

**Error Response**:
```json
{
  "error": "Already serving a client. Complete current service first."
}
```
or
```json
{
  "error": "No clients in queue"
}
```

**Business Logic**:
- Can only call next if not currently serving anyone
- Calls next waiting client based on priority and time
- Updates status from 'waiting' to 'serving'
- Records serving_started_at timestamp

---

### 5. Complete Service

Mark current service as completed.

**Endpoint**: `POST /staff/api/complete/:item_id`

**Authentication**: Required (Staff)

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_id | integer | Yes | Queue item ID |

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**: None

**Request**:
```http
POST /staff/api/complete/44 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
{
  "success": true
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Operation success |

**Status Codes**:
- `200 OK` - Service completed successfully
- `400 Bad Request` - Item not in 'serving' status
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not a staff member
- `404 Not Found` - Queue item not found or not your service

**Error Response**:
```json
{
  "error": "Item is not being served"
}
```

**Business Logic**:
- Can only complete items with status 'serving'
- Updates status to 'completed'
- Records completed_at timestamp
- Calculates actual service time

---

### 6. Skip Client

Mark a client as skipped (no-show).

**Endpoint**: `POST /staff/api/skip/:item_id`

**Authentication**: Required (Staff)

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| item_id | integer | Yes | Queue item ID |

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**: None

**Request**:
```http
POST /staff/api/skip/45 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
{
  "success": true
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Operation success |

**Status Codes**:
- `200 OK` - Client skipped successfully
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not a staff member or wrong service
- `404 Not Found` - Queue item not found

**Business Logic**:
- Updates status to 'skipped'
- Does not record completion time
- Client can join queue again if needed

---

### 7. Get Statistics

Get dashboard statistics for staff member's service.

**Endpoint**: `GET /staff/api/stats`

**Authentication**: Required (Staff)

**Request**:
```http
GET /staff/api/stats HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
{
  "served_today": 12,
  "average_service_time": 18.5,
  "waiting_count": 5
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| served_today | integer | Number of clients served today |
| average_service_time | float | Average service time in minutes |
| waiting_count | integer | Current number waiting |

**Status Codes**:
- `200 OK` - Success
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not a staff member
- `404 Not Found` - Service provider profile not found

---

### 8. Logout

End staff session.

**Endpoint**: `GET /staff/logout`

**Authentication**: Required

**Request**:
```http
GET /staff/logout HTTP/1.1
Host: localhost:5000
Cookie: session=<session_cookie>
```

**Response**: Redirect to `/staff/login`

**Status Codes**:
- `302 Found` - Redirect to login page

---

## ⚙️ ADMIN PANEL APIs

These endpoints require **admin or super admin authentication**.

---

### 1. Admin Login

Authenticate admin and create session.

**Endpoint**: `POST /admin/login`

**Authentication**: None required for this endpoint

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| username | string | Yes | Admin username |
| password | string | Yes | Admin password |

**Request**:
```http
POST /admin/login HTTP/1.1
Host: localhost:5000
Content-Type: application/json

{
  "username": "admin",
  "password": "admin123"
}
```

**Response**:
```json
{
  "success": true,
  "redirect": "/admin/dashboard"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Login success status |
| redirect | string | URL to redirect to (super_admin or admin dashboard) |

**Status Codes**:
- `200 OK` - Login successful
- `401 Unauthorized` - Invalid credentials

**Notes**:
- Accepts both super_admin and admin roles
- Redirects to appropriate dashboard based on role
- Session cookie automatically set

---

### 2. Get Organizations

Get list of organizations (filtered by access level).

**Endpoint**: `GET /admin/api/organizations`

**Authentication**: Required (Admin or Super Admin)

**Request**:
```http
GET /admin/api/organizations HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response** (Super Admin sees all):
```json
[
  {
    "id": 1,
    "name": "King Faisal Hospital",
    "type": "hospital",
    "location": "Kigali",
    "contact_phone": "+250788123456",
    "is_active": true,
    "services_count": 4
  },
  {
    "id": 2,
    "name": "Bank of Kigali",
    "type": "bank",
    "location": "Kigali City",
    "contact_phone": "+250788999888",
    "is_active": true,
    "services_count": 3
  }
]
```

**Response** (Org Admin sees only their organization):
```json
[
  {
    "id": 1,
    "name": "King Faisal Hospital",
    "type": "hospital",
    "location": "Kigali",
    "contact_phone": "+250788123456",
    "is_active": true,
    "services_count": 4
  }
]
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Organization ID |
| name | string | Organization name |
| type | string | Type (hospital, bank, government, other) |
| location | string | Physical location |
| contact_phone | string | Contact number |
| is_active | boolean | Active status |
| services_count | integer | Number of services |

**Status Codes**:
- `200 OK` - Success
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not an admin

**Access Control**:
- Super Admin: Sees all organizations
- Organization Admin: Sees only their organization

---

### 3. Get Services

Get list of services (filtered by organization access).

**Endpoint**: `GET /admin/api/services`

**Authentication**: Required (Admin or Super Admin)

**Request**:
```http
GET /admin/api/services HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "General Consultation",
    "organization_name": "King Faisal Hospital",
    "organization_id": 1,
    "counter_number": "Room 101",
    "estimated_service_time": 20,
    "is_active": true,
    "current_queue_length": 5
  },
  {
    "id": 2,
    "name": "Pharmacy",
    "organization_name": "King Faisal Hospital",
    "organization_id": 1,
    "counter_number": "Counter 1",
    "estimated_service_time": 10,
    "is_active": true,
    "current_queue_length": 2
  }
]
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Service ID |
| name | string | Service name |
| organization_name | string | Organization name |
| organization_id | integer | Organization ID |
| counter_number | string | Counter/Room number |
| estimated_service_time | integer | Estimated time (minutes) |
| is_active | boolean | Active status |
| current_queue_length | integer | Current waiting count |

**Status Codes**:
- `200 OK` - Success
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not an admin

**Access Control**:
- Super Admin: Sees all services
- Organization Admin: Sees only services in their organization

---

### 4. Create Service

Create a new service under an organization.

**Endpoint**: `POST /admin/api/services`

**Authentication**: Required (Admin or Super Admin)

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "Laboratory",
  "organization_id": 1,
  "counter_number": "Lab 1",
  "estimated_service_time": 15
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Service name |
| organization_id | integer | Yes | Organization ID |
| counter_number | string | No | Counter/Room number |
| estimated_service_time | integer | No | Estimated time (default: 15) |

**Request**:
```http
POST /admin/api/services HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>

{
  "name": "Laboratory",
  "organization_id": 1,
  "counter_number": "Lab 1",
  "estimated_service_time": 15
}
```

**Response**:
```json
{
  "success": true,
  "id": 3,
  "message": "Service created successfully"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Operation success |
| id | integer | Created service ID |
| message | string | Success message |

**Status Codes**:
- `200 OK` - Service created successfully
- `400 Bad Request` - Invalid input
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not an admin or cannot manage this organization

**Access Control**:
- Super Admin: Can create service for any organization
- Organization Admin: Can only create services for their organization

---

### 5. Update Service

Update an existing service.

**Endpoint**: `PUT /admin/api/services/:service_id`

**Authentication**: Required (Admin or Super Admin)

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | integer | Yes | Service ID to update |

**Request Headers**:
```
Content-Type: application/json
```

**Request Body**:
```json
{
  "name": "General Consultation - Updated",
  "counter_number": "Room 102",
  "estimated_service_time": 25,
  "is_active": true
}
```

**Request Fields**:
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | No | Service name |
| counter_number | string | No | Counter/Room number |
| estimated_service_time | integer | No | Estimated time (minutes) |
| is_active | boolean | No | Active status |

**Request**:
```http
PUT /admin/api/services/1 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>

{
  "name": "General Consultation - Updated",
  "counter_number": "Room 102"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Service updated"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Operation success |
| message | string | Success message |

**Status Codes**:
- `200 OK` - Service updated successfully
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not an admin or cannot manage this service
- `404 Not Found` - Service not found

**Access Control**:
- Super Admin: Can update any service
- Organization Admin: Can only update services in their organization

---

### 6. Delete Service

Delete a service (and all related queue items).

**Endpoint**: `DELETE /admin/api/services/:service_id`

**Authentication**: Required (Admin or Super Admin)

**URL Parameters**:
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| service_id | integer | Yes | Service ID to delete |

**Request**:
```http
DELETE /admin/api/services/1 HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
{
  "success": true,
  "message": "Service deleted"
}
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| success | boolean | Operation success |
| message | string | Success message |

**Status Codes**:
- `200 OK` - Service deleted successfully
- `401 Unauthorized` - Not logged in
- `403 Forbidden` - Not an admin or cannot manage this service
- `404 Not Found` - Service not found

**Access Control**:
- Super Admin: Can delete any service
- Organization Admin: Can only delete services in their organization

**Warning**: Deleting a service will CASCADE delete all related:
- Queue items
- Service providers
- Analytics data

---

### 7. Get Service Providers

Get list of service providers (staff) filtered by organization.

**Endpoint**: `GET /admin/api/providers`

**Authentication**: Required (Admin or Super Admin)

**Request**:
```http
GET /admin/api/providers HTTP/1.1
Host: localhost:5000
Content-Type: application/json
Cookie: session=<session_cookie>
```

**Response**:
```json
[
  {
    "id": 1,
    "full_name": "Dr. Jane Mugisha",
    "username": "nurse1",
    "email": "nurse1@smartq.rw",
    "phone": "+250788999888",
    "service_name": "General Consultation",
    "service_id": 1,
    "organization_name": "King Faisal Hospital",
    "is_active": true
  }
]
```

**Response Fields**:
| Field | Type | Description |
|-------|------|-------------|
| id | integer | Provider ID |
| full_name | string | Staff member's full name |
| username | string | Login username |