from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sqlite3
import hashlib
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "supersecretkey")
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = False
app.config["SESSION_COOKIE_HTTPONLY"] = True

CORS(app,
     supports_credentials=True,
     resources={r"/*": {"origins": "http://localhost:5173"}},
     allow_headers=["Content-Type"],
     methods=["GET", "POST", "DELETE", "OPTIONS"])

DB_PATH = "solivite.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password: str) -> str:
    salt = os.urandom(16).hex()
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def check_password(password: str, stored: str) -> bool:
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
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
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
            return jsonify({"success": True, "name": user['name'], "email": user['email']})
        else:
            return jsonify({"success": False, "message": "Invalid credentials"}), 401
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/me', methods=['GET'])
def me():
    try:
        user_id = session.get('user_id')
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
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False}), 401

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT email FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        user_email = user['email']

        cursor.execute("""
            SELECT m.*,
                   COALESCE(i.status, 'Pending') as invitation_status,
                   'sender' as role
            FROM moments m
            LEFT JOIN invitations i
                ON i.sender_id = m.user_id
                AND i.schedule_date = m.date
                AND i.schedule_time = m.time
            WHERE m.user_id = ?
            ORDER BY m.id DESC
        """, (user_id,))
        sender_moments = [dict(row) for row in cursor.fetchall()]

        cursor.execute("""
            SELECT
                i.id,
                i.schedule_date as date,
                i.schedule_time as time,
                i.relationship_type as target,
                '' as location,
                i.status as invitation_status,
                u.name as sender_name,
                'receiver' as role
            FROM invitations i
            JOIN users u ON u.id = i.sender_id
            WHERE i.receiver_email = ? AND i.status = 'Accepted'
        """, (user_email,))
        received_moments = [dict(row) for row in cursor.fetchall()]

        conn.close()

        all_moments = sender_moments + received_moments

        return jsonify({"success": True, "moments": all_moments})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/moments', methods=['POST'])
def create_moment():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False}), 401
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO moments (user_id, title, target, location, date, time)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            data.get('title'),
            data.get('target'),
            data.get('location'),
            data.get('date'),
            data.get('time')
        ))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/moments/<int:moment_id>', methods=['DELETE'])
def delete_moment(moment_id):
    try:
        user_id = session.get('user_id')
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

@app.route('/invite', methods=['POST'])
def invite():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        data = request.get_json()
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invitations (sender_id, receiver_email, message, schedule_date, schedule_time, relationship_type, status)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            data.get('receiver_email'),
            data.get('message'),
            data.get('schedule_date'),
            data.get('schedule_time'),
            data.get('relationship_type'),
            'Pending'
        ))
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/invitations/<email>', methods=['GET'])
def get_invites(email):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT invitations.*, users.name AS sender_name
            FROM invitations
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
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE invitations SET status = ? WHERE id = ?",
            (data.get('action'), data.get('invitation_id'))
        )
        conn.commit()
        conn.close()
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({"success": True})

if __name__ == '__main__':
    app.run(port=4000, debug=True)