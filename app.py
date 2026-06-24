from flask import Flask, render_template, request, redirect, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "12345"


# ===== DB =====
def init_db():
    conn = sqlite3.connect("clients.db")
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            service TEXT,
            status TEXT
        )
    """)

    conn.commit()
    conn.close()


def db():
    conn = sqlite3.connect("clients.db")
    return conn


# ===== INIT (ВАЖНО ДЛЯ RAILWAY) =====
with app.app_context():
    init_db()


# ===== LOGIN =====
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if username == "admin" and password == "1234":
            session['user'] = username
            return redirect('/')
        else:
            return "Неверный логин"

    return render_template('login.html')


# ===== LOGOUT =====
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# ===== MAIN =====
@app.route('/')
def index():
    if 'user' not in session:
        return redirect('/login')

    conn = db()
    cur = conn.cursor()

    cur.execute("SELECT * FROM clients")
    clients = cur.fetchall()

    conn.close()

    return render_template('index.html', clients=clients)


# ===== ADD =====
@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    phone = request.form['phone']
    service = request.form['service']
    status = "Новая"

    conn = db()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO clients (name, phone, service, status) VALUES (?, ?, ?, ?)",
        (name, phone, service, status)
    )

    conn.commit()
    conn.close()

    return redirect('/')


# ===== DELETE =====
@app.route('/delete/<int:id>')
def delete(id):
    conn = db()
    cur = conn.cursor()

    cur.execute("DELETE FROM clients WHERE id=?", (id,))

    conn.commit()
    conn.close()

    return redirect('/')


# ===== EDIT =====
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = db()
    cur = conn.cursor()

    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        service = request.form['service']
        status = request.form['status']

        cur.execute("""
            UPDATE clients
            SET name=?, phone=?, service=?, status=?
            WHERE id=?
        """, (name, phone, service, status, id))

        conn.commit()
        conn.close()

        return redirect('/')

    cur.execute("SELECT * FROM clients WHERE id=?", (id,))
    client = cur.fetchone()

    conn.close()

    return render_template('edit.html', client=client)


# ===== START (RAILWAY FIX) =====
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

