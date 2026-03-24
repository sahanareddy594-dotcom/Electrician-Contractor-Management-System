from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# ---------- DATABASE CONNECTION ----------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

# ---------- CREATE TABLES ----------
def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        email TEXT,
        password TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS electricians (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        phone TEXT,
        experience TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS jobs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        location TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        electrician TEXT,
        status TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS materials (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        quantity INTEGER
    )
    """)

    conn.commit()
    conn.close()

init_db()

# ---------- HOME ----------
@app.route("/")
def home():
    return render_template("index.html")

# ---------- REGISTER ----------
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("INSERT INTO users (name, phone, email, password) VALUES (?,?,?,?)",
                       (name, phone, email, password))

        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

# ---------- LOGIN ----------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()

        conn.close()

        if user:
            return redirect("/dashboard")
        else:
            return "Invalid Login"

    return render_template("login.html")

# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    conn = get_db()
    cursor = conn.cursor()

    users = cursor.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    electricians = cursor.execute("SELECT COUNT(*) FROM electricians").fetchone()[0]
    jobs = cursor.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    tasks = cursor.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    conn.close()

    return render_template("dashboard.html",
                           users=users,
                           electricians=electricians,
                           jobs=jobs,
                           tasks=tasks)

# ---------- ELECTRICIANS ----------
@app.route("/electricians", methods=["GET", "POST"])
def electricians():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        exp = request.form['experience']

        cursor.execute("INSERT INTO electricians (name, phone, experience) VALUES (?,?,?)",
                       (name, phone, exp))
        conn.commit()

    data = cursor.execute("SELECT * FROM electricians").fetchall()
    conn.close()

    return render_template("electricians.html", data=data)

# ---------- JOBS ----------
@app.route("/jobs", methods=["GET", "POST"])
def jobs():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form['title']
        location = request.form['location']
        status = request.form['status']

        cursor.execute("INSERT INTO jobs (title, location, status) VALUES (?,?,?)",
                       (title, location, status))
        conn.commit()

    data = cursor.execute("SELECT * FROM jobs").fetchall()
    conn.close()

    return render_template("jobs.html", data=data)

# ---------- TASKS ----------
@app.route("/tasks", methods=["GET", "POST"])
def tasks():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form['name']
        electrician = request.form['electrician']
        status = request.form['status']

        cursor.execute("INSERT INTO tasks (name, electrician, status) VALUES (?,?,?)",
                       (name, electrician, status))
        conn.commit()

    data = cursor.execute("SELECT * FROM tasks").fetchall()
    conn.close()

    return render_template("tasks.html", data=data)

# ---------- MATERIALS ----------
@app.route("/materials", methods=["GET", "POST"])
def materials():
    conn = get_db()
    cursor = conn.cursor()

    if request.method == "POST":
        name = request.form['name']
        quantity = request.form['quantity']

        cursor.execute("INSERT INTO materials (name, quantity) VALUES (?,?)",
                       (name, quantity))
        conn.commit()

    data = cursor.execute("SELECT * FROM materials").fetchall()
    conn.close()

    return render_template("materials.html", data=data)

# ---------- PROFILE ----------
@app.route("/profile", methods=["GET", "POST"])
def profile():
    conn = get_db()
    cursor = conn.cursor()

    user = cursor.execute("SELECT * FROM users LIMIT 1").fetchone()

    if request.method == "POST":
        name = request.form['name']
        phone = request.form['phone']
        email = request.form['email']

        cursor.execute("UPDATE users SET name=?, phone=?, email=? WHERE id=?",
                       (name, phone, email, user[0]))
        conn.commit()

        user = cursor.execute("SELECT * FROM users WHERE id=?", (user[0],)).fetchone()

    conn.close()

    return render_template("profile.html", user=user)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)