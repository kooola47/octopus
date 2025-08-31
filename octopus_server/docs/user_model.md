# 👤 User Model Documentation

## 📋 Table of Contents
- [Overview](#overview)
- [Database Schema](#database-schema)
- [Authentication System](#authentication-system)
- [Authorization System](#authorization-system)
- [User Roles](#user-roles)
- [Session Management](#session-management)
- [Related Documentation](#related-documentation)

---

## 🏁 Overview

The User Model manages user accounts, authentication, and authorization in the Octopus system. It handles user registration, login, role-based access control, and session management.

### Key Responsibilities
- User account management
- Authentication and password security
- Role-based access control (RBAC)
- Session management
- User profile storage

### Related Files
- `models/user_model.py` - Main model implementation
- `routes/auth_routes.py` - Authentication routes
- `routes/user_routes.py` - User management routes
- `routes/user_profile_routes.py` - User profile routes
- `dbhelper.py` - Database operations

---

## 🗄️ Database Schema

The users table stores all user-related information:

```sql
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT,
    password_hash TEXT NOT NULL,
    salt TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    is_active BOOLEAN DEFAULT 1,
    last_login REAL,
    login_attempts INTEGER DEFAULT 0,
    locked_until REAL,
    created_at REAL,
    updated_at REAL
)
```

### Fields Description

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER (Primary Key) | Internal user record ID |
| username | TEXT (Unique) | Unique username |
| email | TEXT | User email address |
| password_hash | TEXT | Hashed user password |
| salt | TEXT | Salt used for password hashing |
| role | TEXT | User role (admin, user, operator, viewer) |
| is_active | BOOLEAN | Account active status |
| last_login | REAL | Timestamp of last login |
| login_attempts | INTEGER | Failed login attempt count |
| locked_until | REAL | Account lockout expiration |
| created_at | REAL | Account creation timestamp |
| updated_at | REAL | Last update timestamp |

### Indexes

- `idx_users_username` - For username lookups
- `idx_users_email` - For email-based queries
- `idx_users_role` - For role-based queries
- `idx_users_is_active` - For active status queries

---

## 🔐 Authentication System

The authentication system handles user login and verification:

### Password Security
- Passwords are hashed using SHA-256 with salt
- Unique salt per user
- Secure hash storage

### Login Process
1. User provides username and password
2. System validates credentials
3. Session is created on successful authentication
4. Login timestamp is updated

### Security Features
- Failed login attempt tracking
- Account lockout after multiple failed attempts
- Session timeout
- Secure password storage

### Authentication Endpoints
- `/login` - Login form and processing
- `/logout` - Session termination
- `/api/auth/status` - Authentication status check

---

## 🛡️ Authorization System

The authorization system controls access based on user roles:

### Role-Based Access Control (RBAC)
- Permissions assigned to roles
- Users assigned to roles
- Access decisions based on role permissions

### Access Control Implementation
- Decorators for route protection
- Role checks in business logic
- UI element visibility based on roles

### Protected Resources
- Administrative functions
- User management
- System configuration
- Sensitive data access

---

## 👥 User Roles

The system supports multiple user roles with different permissions:

### Role Types
1. **Admin** - Full system access
2. **User** - Standard user permissions
3. **Operator** - Task and client management
4. **Viewer** - Read-only access

### Role Permissions

| Role | Dashboard | Tasks | Clients | Users | Plugins | Admin |
|------|-----------|-------|---------|-------|---------|-------|
| Admin | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| User | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| Operator | ✓ | ✓ | ✓ | ✗ | ✓ | ✗ |
| Viewer | ✓ | ✗ | ✗ | ✗ | ✗ | ✗ |

### Role Management
- Role assignment during user creation
- Role changes by administrators
- Role-based UI customization

---

## 🕐 Session Management

Session management handles user login state:

### Session Storage
- Server-side session storage
- Session cookies with secure flags
- Session timeout configuration

### Session Security
- Secure cookie flags
- HTTP-only cookies
- Same-site cookie protection
- Session regeneration on login

### Session Lifecycle
- Creation on successful login
- Validation on each request
- Termination on logout or timeout
- Cleanup of expired sessions

---

## 📚 Related Documentation

### Internal Documentation
- [HOW_TO_ACCESS_USER_PROFILE.md](../HOW_TO_ACCESS_USER_PROFILE.md) - User profile access guide
- [USER_PARAMETERS_GUIDE.md](../USER_PARAMETERS_GUIDE.md) - User parameter management
- [SECURITY_IMPLEMENTATION_COMPLETE.md](../SECURITY_IMPLEMENTATION_COMPLETE.md) - Security implementation details

### External Resources
- [routes/auth_routes.py](../routes/auth_routes.py) - Authentication implementation
- [routes/user_routes.py](../routes/user_routes.py) - User management implementation
- [routes/user_profile_routes.py](../routes/user_profile_routes.py) - User profile implementation
- [Dashboard Documentation](dashboard.md) - User interface for user management
- [API Documentation](api.md) - RESTful endpoints for user data