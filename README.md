# Smart-student-attendance-tracker

## Project Overview

The Student Attendance Management System is a web-based application developed using Flask and SQLite. The system helps educational institutions manage student records and attendance efficiently through a secure admin panel and student portal.

The application allows administrators to manage students, monitor attendance records, and generate reports, while students can log in and mark/view their attendance.

---

## Features

### Admin Module

* Secure Admin Login
* Session Management
* Dashboard Overview
* Add Student
* View Student Records
* Delete Student
* Attendance Reports
* Logout Functionality

### Student Module

* Student Registration
* Student Login
* Student Dashboard
* Attendance Marking
* Attendance History
* Secure Session Handling
* Logout Functionality

### Attendance Features

* Daily Attendance Tracking
* Duplicate Attendance Prevention
* Attendance History
* Location-Based Attendance Verification
* Attendance Reports

---

## Technology Stack

| Technology  | Purpose                   |
| ----------- | ------------------------- |
| Python      | Backend Programming       |
| Flask       | Web Framework             |
| SQLite      | Database                  |
| HTML5       | Frontend Structure        |
| CSS3        | Styling                   |
| Bootstrap 5 | Responsive UI             |
| JavaScript  | Client-side Functionality |
| Git         | Version Control           |
| GitHub      | Repository Hosting        |
| Render      | Cloud Deployment          |

---

## Project Structure

student-attendance-system/

├── app.py

├── database.db

├── requirements.txt

├── README.md

├── static/

│ ├── css/

│ ├── js/

│ └── images/

└── templates/

├── layout.html

├── login.html

├── dashboard.html

├── students.html

├── attendance.html

├── reports.html

├── student_login.html

├── student_register.html

└── student_dashboard.html

---

## Database Design

### Admin Table

| Field    | Type    |
| -------- | ------- |
| id       | INTEGER |
| username | TEXT    |
| password | TEXT    |

### Students Table

| Field      | Type    |
| ---------- | ------- |
| id         | INTEGER |
| student_id | TEXT    |
| name       | TEXT    |
| course     | TEXT    |
| semester   | INTEGER |
| email      | TEXT    |

### Student Users Table

| Field      | Type    |
| ---------- | ------- |
| id         | INTEGER |
| student_id | TEXT    |
| username   | TEXT    |
| password   | TEXT    |

### Attendance Table

| Field           | Type    |
| --------------- | ------- |
| id              | INTEGER |
| student_id      | TEXT    |
| attendance_date | TEXT    |
| status          | TEXT    |

---

## Installation

### Clone Repository

```bash
git clone https://github.com/Manav3322/student-attendance-system.git

cd student-attendance-system
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows:

```bash
venv\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run Application

```bash
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

---

## Default Credentials

### Admin Login

Username:

```text
admin
```

Password:

```text
admin123
```

### Student Login

Student ID:

```text
BCA001
```

Password:

```text
password123
```

---

## Deployment

The application is deployed using Render Cloud Platform.

Deployment Steps:

1. Push source code to GitHub.
2. Connect GitHub repository to Render.
3. Configure Build Command:

```text
pip install -r requirements.txt
```

4. Configure Start Command:

```text
gunicorn app:app
```

5. Deploy the application.

---

## Security Features

* Password Hashing
* Session Management
* Login Authentication
* Duplicate Attendance Prevention
* Attendance Validation
* Secure Logout

---

## Future Enhancements

* Attendance Percentage Calculation
* Student Profile Editing
* CSV Export Reports
* Email Notifications
* QR Code Attendance
* Face Recognition Attendance
* PostgreSQL Database Integration
* Advanced Analytics Dashboard

---

## Author

Manav

Bachelor of Computer Applications (BCA)

Final Year Project

Academic Year 2025–2026

---

## License

This project is developed for academic and educational purposes.
