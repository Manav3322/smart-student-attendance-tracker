from flask import (
    Flask, render_template, request, redirect,
    url_for, flash, session
)
import sqlite3
from datetime import date, timedelta
from werkzeug.security import generate_password_hash, check_password_hash
import math
import os

app = Flask(__name__)


# ==========================================
# APP CONFIGURATION & SESSION SECURITY
# ==========================================
app.config["SECRET_KEY"] = "student_attendance_secret_key"
# This forces the session to automatically expire after 30 minutes of inactivity!
app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=30) 
DB_NAME = "database.db"

# ==========================================
# CONFIGURATION: GEOFENCING (IZee Business School)
# ==========================================
COLLEGE_LAT = 12.7844  
COLLEGE_LNG = 77.6419
ALLOWED_RADIUS_METERS = 200.0 

def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates the distance in meters between two GPS coordinates using the Haversine formula."""
    R = 6371000  # Radius of Earth in meters
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    
    a = math.sin(delta_phi / 2.0) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * \
        math.sin(delta_lambda / 2.0) ** 2
    
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance


# ==========================================
# DATABASE HELPER FUNCTIONS
# ==========================================
def get_db_connection():
    """Helper function to get database connection."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_database():
    """Create database and required tables if they don't exist."""
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS admin (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            course TEXT NOT NULL,
            semester INTEGER NOT NULL,
            email TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS student_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            attendance_date TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # Insert Default Admin Account
    admin = cursor.execute("SELECT * FROM admin WHERE username = ?", ("admin",)).fetchone()
    if not admin:
        hashed_password = generate_password_hash("admin123")
        cursor.execute("INSERT INTO admin (username, password) VALUES (?, ?)", ("admin", hashed_password))

    # Insert Default Student Data
    student = cursor.execute("SELECT * FROM student_users WHERE student_id = ?", ("BCA001",)).fetchone()
    if not student:
        hashed_password = generate_password_hash("password123")
        cursor.execute("INSERT INTO student_users (student_id, username, password) VALUES (?, ?, ?)", ("BCA001", "BCA001", hashed_password))
        cursor.execute("INSERT INTO students (student_id, name, course, semester, email) VALUES (?, ?, ?, ?, ?)", ("BCA001", "Default Student", "BCA", 6, "student@izee.edu"))

    conn.commit()
    conn.close()


# ==========================================
# ADMIN ROUTES
# ==========================================
@app.route("/", methods=["GET", "POST"])
def login():
    """Admin Login Route"""
    if "admin_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admin WHERE username = ?", (username,)).fetchone()
        conn.close()

        if admin and check_password_hash(admin["password"], password):
            session.permanent = True 
            session["admin_id"] = admin["id"]
            session["username"] = admin["username"]
            flash("Admin login successful.", "success")
            return redirect(url_for("dashboard"))
        
        flash("Invalid admin username or password.", "danger")

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "admin_id" not in session:
        flash("Please log in to access the dashboard.", "warning")
        return redirect(url_for("login"))

    conn = get_db_connection()
    total_students = conn.execute("SELECT COUNT(*) FROM students").fetchone()[0]
    total_attendance = conn.execute("SELECT COUNT(*) FROM attendance").fetchone()[0]
    conn.close()

    return render_template("dashboard.html", total_students=total_students, total_attendance=total_attendance)


@app.route("/students", methods=["GET", "POST"])
def students():
    if "admin_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    if request.method == "POST":
        student_id = request.form["student_id"].strip()
        name = request.form["name"]
        course = request.form["course"]
        semester = request.form["semester"]
        email = request.form["email"]

        existing = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
        if existing:
            flash(f"Student ID {student_id} already exists.", "danger")
        else:
            conn.execute("INSERT INTO students (student_id, name, course, semester, email) VALUES (?, ?, ?, ?, ?)", (student_id, name, course, semester, email))
            default_password_hash = generate_password_hash("password123")
            conn.execute("INSERT INTO student_users (student_id, username, password) VALUES (?, ?, ?)", (student_id, student_id, default_password_hash))
            conn.commit()
            flash(f"Student added! Login with Student ID and password 'password123'", "success")

    all_students = conn.execute("SELECT * FROM students ORDER BY id DESC").fetchall()
    conn.close()

    return render_template("students.html", students=all_students)


@app.route("/delete_student/<int:id>")
def delete_student(id):
    if "admin_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    student = conn.execute("SELECT student_id FROM students WHERE id = ?", (id,)).fetchone()
    if student:
        actual_student_id = student["student_id"]
        conn.execute("DELETE FROM students WHERE id = ?", (id,))
        conn.execute("DELETE FROM student_users WHERE student_id = ?", (actual_student_id,))
        conn.execute("DELETE FROM attendance WHERE student_id = ?", (actual_student_id,))
        conn.commit()
        flash("Student deleted successfully.", "success")
    
    conn.close()
    return redirect(url_for("students"))


@app.route("/reports")
def reports():
    if "admin_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    query = """
        SELECT a.attendance_date, a.status, s.student_id, s.name, s.course 
        FROM attendance a
        JOIN students s ON a.student_id = s.student_id
        ORDER BY a.attendance_date DESC
    """
    records = conn.execute(query).fetchall()
    conn.close()

    return render_template("reports.html", records=records)


@app.route("/logout")
def logout():
    session.clear() # Clears everything safely
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))


# ==========================================
# STUDENT ROUTES
# ==========================================
@app.route("/student-register", methods=["GET", "POST"])
def student_register():
    if request.method == "POST":
        student_id = request.form["student_id"].strip()
        name = request.form["name"].strip()
        course = request.form["course"].strip()
        semester = request.form["semester"]
        email = request.form["email"].strip()
        password = request.form["password"]

        conn = get_db_connection()
        existing = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
        
        if existing:
            flash("An account with this Student ID already exists. Please login.", "warning")
            conn.close()
            return redirect(url_for("student_login"))
        
        hashed_password = generate_password_hash(password)
        conn.execute("INSERT INTO students (student_id, name, course, semester, email) VALUES (?, ?, ?, ?, ?)", (student_id, name, course, semester, email))
        conn.execute("INSERT INTO student_users (student_id, username, password) VALUES (?, ?, ?)", (student_id, student_id, hashed_password))
        conn.commit()
        conn.close()
        
        flash("Account created successfully! You can now log in.", "success")
        return redirect(url_for("student_login"))

    return render_template("student_register.html")


@app.route("/student-login", methods=["GET", "POST"])
def student_login():
    if "student_id" in session:
        return redirect(url_for("student_dashboard"))

    if request.method == "POST":
        student_id_input = request.form["student_id"].strip() 
        password = request.form["password"]

        conn = get_db_connection()
        student = conn.execute("SELECT * FROM student_users WHERE student_id = ?", (student_id_input,)).fetchone()
        conn.close()

        if student and check_password_hash(student["password"], password):
            session.permanent = True 
            session["student_id"] = student["student_id"] 
            session["student_username"] = student["username"]
            flash("Welcome back!", "success")
            return redirect(url_for("student_dashboard"))

        flash("Invalid student credentials. Use your exact Student ID.", "danger")

    return render_template("student_login.html")


@app.route("/student-dashboard")
def student_dashboard():
    if "student_id" not in session:
        return redirect(url_for("student_login"))

    conn = get_db_connection()
    student_id = session["student_id"]
    
    profile = conn.execute("SELECT * FROM students WHERE student_id = ?", (student_id,)).fetchone()
    total_present = conn.execute("SELECT COUNT(*) FROM attendance WHERE student_id = ? AND status LIKE 'Present%'", (student_id,)).fetchone()[0]
    conn.close()

    return render_template("student_dashboard.html", profile=profile, total_present=total_present)


@app.route("/attendance", methods=["GET", "POST"])
def attendance():
    if "student_id" not in session:
        return redirect(url_for("student_login"))

    student_id = session["student_id"]
    conn = get_db_connection()
    today_date = date.today().strftime('%Y-%m-%d')
    SECRET_CLASS_CODE = "IZEE99"

    if request.method == "POST":
        existing = conn.execute("SELECT * FROM attendance WHERE student_id = ? AND attendance_date = ?", (student_id, today_date)).fetchone()
        if existing:
            flash("You have already marked your attendance for today.", "warning")
            conn.close()
            return redirect(url_for("attendance"))

        # OVERRIDE LOGIC
        override_code = request.form.get("override_code")
        if override_code:
            if override_code.strip().upper() == SECRET_CLASS_CODE:
                conn.execute("INSERT INTO attendance (student_id, attendance_date, status) VALUES (?, ?, 'Present (Code Override)')", (student_id, today_date))
                conn.commit()
                flash("Attendance marked successfully using the Class Code!", "success")
            else:
                flash("Invalid Class Code. Attendance denied.", "danger")
            conn.close()
            return redirect(url_for("attendance"))

        # GPS LOGIC
        try:
            student_lat = float(request.form.get("latitude", 0))
            student_lng = float(request.form.get("longitude", 0))
        except ValueError:
            flash("Invalid GPS coordinates received.", "danger")
            conn.close()
            return redirect(url_for("attendance"))

        distance = calculate_distance(COLLEGE_LAT, COLLEGE_LNG, student_lat, student_lng)
        
        if distance > ALLOWED_RADIUS_METERS:
            flash(f"Attendance denied! You are {int(distance)} meters away from campus. You must be within {int(ALLOWED_RADIUS_METERS)} meters.", "danger")
            conn.close()
            return redirect(url_for("attendance"))

        conn.execute("INSERT INTO attendance (student_id, attendance_date, status) VALUES (?, ?, 'Present')", (student_id, today_date))
        conn.commit()
        flash("Attendance marked successfully! Location Verified.", "success")
        conn.close()
        return redirect(url_for("attendance"))

    history = conn.execute("SELECT attendance_date, status FROM attendance WHERE student_id = ? ORDER BY attendance_date DESC", (student_id,)).fetchall()
    conn.close()

    return render_template("attendance.html", history=history, today=today_date)


@app.route("/student-logout")
def student_logout():
    session.clear() 
    flash("Student logged out.", "info")
    return redirect(url_for("student_login"))


# Create database when app loads
create_database()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)