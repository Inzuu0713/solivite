import sqlite3

def merge():
    src_conn = sqlite3.connect('solivite.db')
    src_conn.row_factory = sqlite3.Row
    src_c = src_conn.cursor()

    dst_conn = sqlite3.connect('src/database/solivite.db')
    dst_c = dst_conn.cursor()

    # Get max user id in dst
    dst_c.execute("SELECT MAX(id) FROM users")
    max_user_id = dst_c.fetchone()[0] or 0

    # We will offset all IDs from src by max_user_id
    offset = max_user_id

    # 1. Users
    users = src_c.execute("SELECT * FROM users").fetchall()
    for u in users:
        new_id = u['id'] + offset
        try:
            dst_c.execute("INSERT INTO users (id, name, email, password) VALUES (?, ?, ?, ?)", 
                          (new_id, u['name'], u['email'], u['password']))
        except sqlite3.IntegrityError:
            pass # Email already exists

    # 2. Moments
    try:
        moments = src_c.execute("SELECT * FROM moments").fetchall()
        for m in moments:
            new_user_id = m['user_id'] + offset
            dst_c.execute("INSERT INTO moments (user_id, title, target, location, date, time) VALUES (?, ?, ?, ?, ?, ?)",
                          (new_user_id, m['title'], m['target'], m['location'], m['date'], m['time']))
    except Exception as e:
        print("Moments error:", e)

    # 3. Invitations
    try:
        invitations = src_c.execute("SELECT * FROM invitations").fetchall()
        for i in invitations:
            new_sender_id = i['sender_id'] + offset
            keys = i.keys()
            loc = i['location'] if 'location' in keys else ''
            dst_c.execute("""
                INSERT INTO invitations (sender_id, receiver_email, message, location, schedule_date, schedule_time, relationship_type, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (new_sender_id, i['receiver_email'], i['message'], loc, i['schedule_date'], i['schedule_time'], i['relationship_type'], i['status']))
    except Exception as e:
        print("Invitations error:", e)

    # 4. Memories
    try:
        memories = src_c.execute("SELECT * FROM memories").fetchall()
        for mem in memories:
            new_user_id = mem['user_id'] + offset
            dst_c.execute("INSERT INTO memories (user_id, url, caption, companion, date) VALUES (?, ?, ?, ?, ?)",
                          (new_user_id, mem['url'], mem['caption'], mem['companion'], mem['date']))
    except Exception as e:
        print("Memories error:", e)

    dst_conn.commit()
    print("Merged successfully")

if __name__ == '__main__':
    merge()
