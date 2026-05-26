from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import os
import smtplib
import threading
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()

try:
    import psycopg2
    from psycopg2 import IntegrityError as PgIntegrityError
    import psycopg2.extras
except ImportError:
    psycopg2 = None
    class PgIntegrityError(Exception): pass

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
app.config["SESSION_COOKIE_SAMESITE"] = "None"
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_HTTPONLY"] = True

FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

CORS(app,
     supports_credentials=True,
     resources={r"/*": {"origins": FRONTEND_URL}},
     allow_headers=["Content-Type", "X-User-Id"],
     methods=["GET", "POST", "DELETE", "PUT", "OPTIONS"])

DB_URL = os.environ.get("DATABASE_URL")
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "solivite.db")

class CursorWrapper:
    def __init__(self, cursor, is_pg):
        self.cursor = cursor
        self.is_pg = is_pg

    def execute(self, query, params=None):
        if self.is_pg:
            if params:
                query = query.replace('?', '%s')
        if params is None:
            return self.cursor.execute(query)
        return self.cursor.execute(query, params)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def executescript(self, script):
        if self.is_pg:
            script = script.replace('AUTOINCREMENT', 'SERIAL')
            script = script.replace('INTEGER PRIMARY KEY SERIAL', 'SERIAL PRIMARY KEY')
            return self.cursor.execute(script)
        else:
            return self.cursor.executescript(script)

class ConnectionWrapper:
    def __init__(self, conn, is_pg):
        self.conn = conn
        self.is_pg = is_pg

    def cursor(self):
        return CursorWrapper(self.conn.cursor(), self.is_pg)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

def get_db_connection():
    if DB_URL and psycopg2:
        conn = psycopg2.connect(DB_URL)
        conn.cursor_factory = psycopg2.extras.RealDictCursor
        return ConnectionWrapper(conn, True)
    else:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return ConnectionWrapper(conn, False)

def get_user_id():
    return session.get('user_id') or request.headers.get('X-User-Id')

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            name     TEXT    NOT NULL,
            email    TEXT    NOT NULL UNIQUE,
            password TEXT    NOT NULL
        );
        CREATE TABLE IF NOT EXISTS moments (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            title    TEXT,
            target   TEXT,
            location TEXT,
            date     TEXT,
            time     TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS invitations (
            id                INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id         INTEGER NOT NULL,
            receiver_email    TEXT    NOT NULL,
            message           TEXT,
            location          TEXT,
            schedule_date     TEXT,
            schedule_time     TEXT,
            relationship_type TEXT,
            status            TEXT    NOT NULL DEFAULT 'Pending',
            FOREIGN KEY (sender_id) REFERENCES users(id)
        );
        CREATE TABLE IF NOT EXISTS memories (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id   INTEGER NOT NULL,
            url       TEXT    NOT NULL,
            caption   TEXT,
            companion TEXT,
            date      TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    conn.close()

init_db()

SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASS = os.environ.get("SMTP_PASS", "")

def _send_email_worker(to_address, subject, html_content):
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print(f"MOCK EMAIL TO: {to_address} | SUBJECT: {subject}")
        return
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = SMTP_USER
        msg['To'] = to_address
        msg.set_content('Please view this email in an HTML-compatible email client.')
        msg.add_alternative(html_content, subtype='html')
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_email(to_address, subject, html_content):
    t = threading.Thread(target=_send_email_worker, args=(to_address, subject, html_content), daemon=True)
    t.start()

def hash_password(password):
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def check_password(password, stored):
    salt, hashed = stored.split("$", 1)
    return hashlib.sha256((salt + password).encode()).hexdigest() == hashed

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        hashed_pw = hash_password(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)", (name, email, hashed_pw))
        conn.commit()
        conn.close()
        send_email(email, "Welcome to Solivite!", f"Hello {name}, welcome to Solivite!")
        return jsonify({"success": True})
    except (sqlite3.IntegrityError, PgIntegrityError):
        return jsonify({"success": False, "message": "Email already exists"}), 409
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        if user and check_password(password, user['password']):
            session['user_id'] = user['id']
            return jsonify({"success": True, "name": user['name'], "email": user['email'], "user_id": user['id']})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/me', methods=['GET'])
def me():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return jsonify({"success": True, "user": dict(user)})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/moments', methods=['GET'])
def get_moments():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        user_email = user['email']
        cursor.execute("""
            SELECT m.*, i.receiver_email, i.message as message,
                   COALESCE(i.status, 'Pending') as invitation_status, 'sender' as role
            FROM moments m
            LEFT JOIN invitations i ON i.sender_id = m.user_id
                AND i.schedule_date = m.date AND i.schedule_time = m.time
            WHERE m.user_id = ? ORDER BY m.id DESC
        """, (user_id,))
        sender_moments = [dict(row) for row in cursor.fetchall()]
        cursor.execute("""
            SELECT i.id, i.schedule_date as date, i.schedule_time as time,
                   i.relationship_type as target, i.location, i.message,
                   i.status as invitation_status, u.name as sender_name, 'receiver' as role
            FROM invitations i JOIN users u ON u.id = i.sender_id
            WHERE i.receiver_email = ? AND i.status = 'Accepted'
        """, (user_email,))
        received_moments = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"success": True, "moments": sender_moments + received_moments})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/moments', methods=['POST'])
def create_moment():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO moments (user_id, title, target, location, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, data.get('title'), data.get('target'), data.get('location'), data.get('date'), data.get('time')))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/moments/<int:moment_id>', methods=['DELETE'])
def delete_moment(moment_id):
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM moments WHERE id = ? AND user_id = ?", (moment_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/moments/<int:moment_id>', methods=['PUT'])
def update_moment(moment_id):
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE moments SET title=?, target=?, location=?, date=?, time=?
            WHERE id=? AND user_id=?
        """, (data.get('title'), data.get('target'), data.get('location'), data.get('date'), data.get('time'), moment_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/invite', methods=['POST'])
def invite():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.get_json()
        location = data.get('location', '')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invitations (sender_id, receiver_email, message, location, schedule_date, schedule_time, relationship_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, data.get('receiver_email'), data.get('message'), location,
              data.get('schedule_date'), data.get('schedule_time'), data.get('relationship_type'), 'Pending'))
        conn.commit()
        conn.close()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
        sender = cursor.fetchone()
        conn.close()
        if sender:
            maps_url = f"https://www.google.com/maps/search/?api=1&query={location.replace(' ', '+')}"
            receiver_html = f"<p>Hi! {sender['name']} invited you to a moment at {location} on {data.get('schedule_date')} at {data.get('schedule_time')}.</p>"
            send_email(data.get('receiver_email'), f"Invitation from {sender['name']}!", receiver_html)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/invitations/<email>', methods=['GET'])
def get_invites(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invitations.*, users.name AS sender_name FROM invitations
            JOIN users ON users.id = invitations.sender_id
            WHERE receiver_email = ? AND status = 'Pending'
        """, (email,))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"success": True, "invitations": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/invitations/respond', methods=['POST'])
def respond():
    try:
        data = request.get_json()
        action = data.get('action')
        invitation_id = data.get('invitation_id')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE invitations SET status = ? WHERE id = ?", (action, invitation_id))
        conn.commit()
        cursor.execute("""
            SELECT i.*, u.name AS sender_name, u.email AS sender_email
            FROM invitations i JOIN users u ON u.id = i.sender_id WHERE i.id = ?
        """, (invitation_id,))
        inv = cursor.fetchone()
        conn.close()
        if inv:
            notify_html = f"<p>Your invitation was {action} by {inv['receiver_email']}.</p>"
            send_email(inv['sender_email'], f"Your invitation was {action}!", notify_html)
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/memories', methods=['GET'])
def get_memories():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        if not user:
            return jsonify({"success": False}), 401
        cursor.execute("""
            SELECT * FROM memories WHERE user_id=? OR companion=? OR companion=? ORDER BY id DESC
        """, (user_id, user['email'], user['name']))
        rows = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return jsonify({"success": True, "memories": rows})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/memories', methods=['POST'])
def create_memory():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO memories (user_id, url, caption, companion, date) VALUES (?, ?, ?, ?, ?)
        """, (user_id, data.get('url'), data.get('caption'), data.get('companion'), data.get('date')))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/memories/<int:mem_id>', methods=['PUT'])
def update_memory(mem_id):
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE memories SET caption=?, companion=? WHERE id=? AND user_id=?",
                       (data.get('caption'), data.get('companion'), mem_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/memories/<int:mem_id>', methods=['DELETE'])
def delete_memory(mem_id):
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False}), 401
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM memories WHERE id=? AND user_id=?", (mem_id, user_id))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/reply', methods=['POST'])
def reply_to_declined():
    try:
        user_id = get_user_id()
        if not user_id:
            return jsonify({"success": False, "message": "Not authenticated"}), 401
        data = request.get_json()
        receiver_email = data.get('receiver_email')
        message = data.get('message')
        if not receiver_email or not message:
            return jsonify({"success": False, "message": "Missing email or message"}), 400
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name, email FROM users WHERE id = ?", (user_id,))
        sender = cursor.fetchone()
        conn.close()
        send_email(receiver_email, f"Reply from {sender['name']}", f"Message: {message}")
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})
    
@app.route('/admin/users', methods=['GET'])
def admin_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return jsonify({"users": users})

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=False)
