from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""CREATE TABLE IF NOT EXISTS electricians(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, phone TEXT, experience TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS jobs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, location TEXT, deadline TEXT, electrician_id INTEGER)""")

    c.execute("""CREATE TABLE IF NOT EXISTS tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, job_id INTEGER, electrician_id INTEGER, status TEXT)""")

    c.execute("""CREATE TABLE IF NOT EXISTS materials(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT, quantity INTEGER, used INTEGER)""")

    conn.commit()
    conn.close()

init_db()

# ---------- DASHBOARD ----------
@app.route("/")
def dashboard():
    conn = get_db()
    c = conn.cursor()

    e = c.execute("SELECT COUNT(*) FROM electricians").fetchone()[0]
    j = c.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    t = c.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]

    conn.close()
    return render_template("dashboard.html", e=e, j=j, t=t)

# ---------- ELECTRICIANS ----------
@app.route("/electricians", methods=["GET","POST"])
def electricians():
    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        c.execute("INSERT INTO electricians(name,phone,experience) VALUES(?,?,?)",
                  (request.form['name'], request.form['phone'], request.form['experience']))
        conn.commit()

    data = c.execute("SELECT * FROM electricians").fetchall()
    conn.close()
    return render_template("electricians.html", data=data)

@app.route("/delete_electrician/<int:id>")
def delete_electrician(id):
    conn = get_db()
    conn.execute("DELETE FROM electricians WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/electricians")

# ---------- JOBS ----------
@app.route("/jobs", methods=["GET","POST"])
def jobs():
    conn = get_db()
    c = conn.cursor()

    electricians = c.execute("SELECT * FROM electricians").fetchall()

    if request.method == "POST":
        c.execute("INSERT INTO jobs(title,location,deadline,electrician_id) VALUES(?,?,?,?)",
                  (request.form['title'], request.form['location'],
                   request.form['deadline'], request.form['electrician']))
        conn.commit()

    data = c.execute("""
        SELECT jobs.*, electricians.name as ename
        FROM jobs LEFT JOIN electricians
        ON jobs.electrician_id = electricians.id
    """).fetchall()

    conn.close()
    return render_template("jobs.html", data=data, electricians=electricians)

# ---------- TASKS ----------
@app.route("/tasks", methods=["GET","POST"])
def tasks():
    conn = get_db()
    c = conn.cursor()

    jobs = c.execute("SELECT * FROM jobs").fetchall()
    electricians = c.execute("SELECT * FROM electricians").fetchall()

    if request.method == "POST":
        c.execute("INSERT INTO tasks(name,job_id,electrician_id,status) VALUES(?,?,?,?)",
                  (request.form['name'], request.form['job'],
                   request.form['electrician'], request.form['status']))
        conn.commit()

    data = c.execute("""
        SELECT tasks.*, jobs.title as jobname, electricians.name as ename
        FROM tasks
        LEFT JOIN jobs ON tasks.job_id = jobs.id
        LEFT JOIN electricians ON tasks.electrician_id = electricians.id
    """).fetchall()

    conn.close()
    return render_template("tasks.html", data=data, jobs=jobs, electricians=electricians)

# ---------- MATERIALS ----------
@app.route("/materials", methods=["GET","POST"])
def materials():
    conn = get_db()
    c = conn.cursor()

    if request.method == "POST":
        c.execute("INSERT INTO materials(name,quantity,used) VALUES(?,?,?)",
                  (request.form['name'], request.form['quantity'], request.form['used']))
        conn.commit()

    data = c.execute("SELECT * FROM materials").fetchall()
    conn.close()
    return render_template("materials.html", data=data)

# ---------- RUN ----------
if __name__ == "__main__":
    app.run(debug=True)