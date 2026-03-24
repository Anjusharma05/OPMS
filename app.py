from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secret123"

# ---------------- DATABASE ----------------
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            password TEXT,
            role TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            recruiter_email TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_email TEXT,
            job_id INTEGER
        )
    ''')

    conn.commit()
    conn.close()
init_db()

# ---------------- HOME ----------------
@app.route('/')
def home():
    return "OPMS is running 🚀"

# ---------------- LOGIN ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['email'] = email
            session['role'] = user[3]

            if user[3] == 'student':
                return redirect('/student')
            elif user[3] == 'recruiter':
                return redirect('/recruiter')
            elif user[3] == 'admin':
                return redirect('/admin')
        else:
            return "❌ Invalid email or password"

    return render_template('login.html')

# ---------------- REGISTER ----------------
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (email, password, role) VALUES (?, ?, ?)",
                       (email, password, role))

        conn.commit()
        conn.close()

        return "✅ User registered successfully!"

    return render_template('register.html')

# ---------------- STUDENT DASHBOARD ----------------
@app.route('/student')
def student():
    if 'email' not in session or session['role'] != 'student':
        return redirect('/login')
    return render_template('student.html')

# ---------------- RECRUITER DASHBOARD ----------------
@app.route('/recruiter')
def recruiter():
    if 'email' not in session or session['role'] != 'recruiter':
        return redirect('/login')
    return render_template('recruiter.html')

# ---------------- ADMIN DASHBOARD ----------------
@app.route('/admin')
def admin():
    if 'email' not in session or session['role'] != 'admin':
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    conn.close()

    return render_template('admin.html', users=users, jobs=jobs)

# ---------------- POST JOB ----------------
@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if 'email' not in session or session['role'] != 'recruiter':
        return redirect('/login')

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']

        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO jobs (title, description, recruiter_email) VALUES (?, ?, ?)",
            (title, description, session['email'])
        )

        conn.commit()
        conn.close()

        return "✅ Job posted successfully!"

    return render_template('post_job.html')

# ---------------- VIEW JOBS ----------------
@app.route('/jobs')
def jobs():
    if 'email' not in session or session['role'] != 'student':
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs")
    jobs = cursor.fetchall()

    conn.close()

    return render_template('jobs.html', jobs=jobs)

# ---------------- APPLY ----------------
@app.route('/apply/<int:job_id>')
def apply(job_id):
    if 'email' not in session or session['role'] != 'student':
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO applications (student_email, job_id) VALUES (?, ?)",
        (session['email'], job_id)
    )

    conn.commit()
    conn.close()

    return "✅ Applied successfully!"

# ---------------- LOGOUT ----------------
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

# ---------------- RUN ----------------
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)
