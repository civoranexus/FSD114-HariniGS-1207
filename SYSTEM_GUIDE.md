# EduVillage Dynamic Login & Registration System

## Overview
The system now supports dynamic user registration and login without any predefined values. New users can create accounts and login with their credentials.

## How It Works

### 1. NEW USER REGISTRATION (First Time)
**URL:** `http://127.0.0.1:8000/accounts/register/`

**Steps:**
1. Click "Create Account" or go to the register page
2. Fill in the form:
   - **Username:** Your unique username
   - **Email:** Your email address
   - **Password:** Minimum 6 characters
   - **Confirm Password:** Must match the password
   - **Role:** Choose between Student or Teacher
3. Click "Create Account"
4. You'll be redirected to login page
5. Login with your new credentials

**Example:**
- Username: john_student
- Email: john@example.com
- Password: mypassword123
- Role: Student

---

### 2. EXISTING USER LOGIN
**URL:** `http://127.0.0.1:8000/accounts/login/`

**Steps:**
1. Enter your username
2. Enter your password
3. Select your role (must match the role you registered with)
4. Click "Login"
5. You'll be automatically redirected to your dashboard:
   - **Student** → Student Dashboard (`/courses/dashboard/student/`)
   - **Teacher** → Teacher Dashboard (`/courses/dashboard/teacher/`)
   - **Admin** → Admin Dashboard (`/admin/`)

**Important:** The role you select MUST match the role you registered with!

---

### 3. LOGOUT
**Location:** Navbar (top right)
- Click your username and select "Logout"
- You'll be redirected to home page

---

## Data Flow

```
┌─────────────────┐
│  User Visits    │
│  /register/     │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────────┐
│  Fill Registration Form         │
│  - Username (unique)            │
│  - Email (unique)               │
│  - Password (min 6 chars)       │
│  - Role (Student/Teacher)       │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│  System Creates:                │
│  ✓ User account                 │
│  ✓ Profile with role            │
│  ✓ Django signal auto-setup     │
└────────┬────────────────────────┘
         │
         ▼
┌─────────────────┐
│ Redirected to   │
│ Login Page      │
└────────┬────────┘
         │
         ▼
┌──────────────────────────────────┐
│  User Logs In                    │
│  - Enter username & password     │
│  - Select matching role          │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  System Verifies:                │
│  ✓ Username exists               │
│  ✓ Password correct              │
│  ✓ Role matches profile          │
└────────┬─────────────────────────┘
         │
         ▼
┌──────────────────────────────────┐
│  Auto-Redirect to Dashboard      │
│  Based on Role                   │
└──────────────────────────────────┘
```

---

## Features

✅ **Dynamic User Registration** - Create new accounts anytime
✅ **Role-Based Authentication** - Different dashboards for different roles
✅ **Secure Password Storage** - Django password hashing
✅ **Session Management** - Automatic login/logout
✅ **Email Validation** - Unique email per user
✅ **Username Validation** - Unique username per user
✅ **Error Messages** - Clear feedback on validation failures
✅ **Auto-Redirect** - Smart redirection based on role

---

## Testing Scenarios

### Scenario 1: New Student Registration
1. Go to `/accounts/register/`
2. Register with role "Student"
3. Login with same credentials
4. Verify you're redirected to Student Dashboard

### Scenario 2: New Teacher Registration
1. Go to `/accounts/register/`
2. Register with role "Teacher"
3. Login with same credentials
4. Verify you're redirected to Teacher Dashboard

### Scenario 3: Wrong Role Login
1. Register as Student
2. Try to login as Teacher
3. You'll see error: "Invalid role for this user"

### Scenario 4: Invalid Credentials
1. Try to login with wrong password
2. You'll see error: "Invalid username or password"

---

## Database Structure

**Users Table:**
- username (unique)
- email (unique)
- password (hashed)

**Profiles Table:**
- user (OneToOne relationship)
- role (student/teacher/admin)

---

## System Flow Summary

1. **Registration:** User creates account with username, email, password, and role
2. **Django Signal:** Automatically creates Profile when User is created
3. **Role Assignment:** Register view updates Profile with user's selected role
4. **Login:** User authenticates with username/password
5. **Verification:** System checks if role matches user's profile
6. **Redirect:** Auto-redirect to appropriate dashboard based on role
7. **Logout:** Session clears, user redirected to home

---

## Troubleshooting

**Problem:** "Invalid role for this user"
- **Solution:** Make sure you select the same role you registered with

**Problem:** "Username already exists"
- **Solution:** Choose a different username

**Problem:** "Email already registered"
- **Solution:** Use a different email address

**Problem:** "Passwords do not match"
- **Solution:** Make sure both password fields are identical

**Problem:** "Invalid username or password"
- **Solution:** Check your username and password are correct

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/accounts/register/` | GET, POST | Register new user |
| `/accounts/login/` | GET, POST | Login existing user |
| `/accounts/logout/` | GET | Logout current user |
| `/courses/dashboard/student/` | GET | Student Dashboard (auth required) |
| `/courses/dashboard/teacher/` | GET | Teacher Dashboard (auth required) |

---

## Notes

- The system works COMPLETELY DYNAMICALLY without any predefined users
- Any new user can register and login
- The role-based redirection ensures each user type sees their correct dashboard
- All validation is built-in and provides helpful error messages
- The system is production-ready with proper security measures
