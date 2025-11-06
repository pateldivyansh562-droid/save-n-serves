import mysql.connector
from flask import Flask, request, jsonify, send_from_directory
import time

app = Flask(__name__, static_folder='.', static_url_path='')

# --- CONFIGURATION ---
MYSQL_CONFIG = {
    'user': 'root',
    'password': 'tiger', # <-- UPDATE THIS
    'host': 'localhost',
    'database': 'savenserve_db'
}

def get_db():
    try:
        return mysql.connector.connect(**MYSQL_CONFIG)
    except Exception as e:
        print("DB Connection Error:", e)
        return None

# --- AUTHENTICATION ---
@app.route('/api/signup', methods=['POST'])
def signup():
    data = request.json
    conn = get_db()
    if not conn: return jsonify({"success": False, "message": "DB error"}), 500
    cursor = conn.cursor()
    try:
        # Try to insert new user. The UNIQUE constraint on 'username' in SQL 
        # will automatically fail if the username exists.
        cursor.execute("INSERT INTO users (name, username, password, role) VALUES (%s, %s, %s, %s)",
                       (data['name'], data['username'], data['password'], data['role']))
        conn.commit()
        return jsonify({"success": True, "message": "Account created successfully."})
    except mysql.connector.IntegrityError:
        return jsonify({"success": False, "message": "Username already taken."}), 409
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/login', methods=['POST'])
def login():
    data = request.json
    conn = get_db()
    if not conn: return jsonify({"success": False, "message": "DB error"}), 500
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, name, username, role FROM users WHERE username = %s AND password = %s",
                   (data['username'], data['password']))
    user = cursor.fetchone()
    conn.close()
    if user: return jsonify({"success": True, "user": user})
    return jsonify({"success": False, "message": "Invalid credentials."}), 401

# --- DUAL-USER CORE ENDPOINTS ---
@app.route('/api/donate', methods=['POST'])
def donate():
    # Staff posts a donation
    data = request.json
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("INSERT INTO donations (donor_name, quantity, location, status) VALUES (%s, %s, %s, 'pending')",
                   (data['donor'], data['qty'], data['location']))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Donation posted for NGOs."})

@app.route('/api/request-food', methods=['POST'])
def request_food():
    # NGO posts a request
    data = request.json
    conn = get_db(); cursor = conn.cursor()
    cursor.execute("INSERT INTO food_requests (name, organization, quantity, location, status) VALUES (%s, %s, %s, %s, 'pending')",
                   (data['name'], data.get('org',''), data['qty'], data['location']))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Request sent to Staff."})

@app.route('/api/ngo/pending', methods=['GET'])
def ngo_pending():
    # NGOs see pending DONATIONS
    conn = get_db(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM donations WHERE status='pending' ORDER BY created_at DESC")
    data = cursor.fetchall(); conn.close()
    return jsonify(data)

@app.route('/api/staff/pending', methods=['GET'])
def staff_pending():
    # Staff see pending REQUESTS
    conn = get_db(); cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM food_requests WHERE status='pending' ORDER BY created_at DESC")
    data = cursor.fetchall(); conn.close()
    return jsonify(data)

@app.route('/api/update-status', methods=['POST'])
def update_status():
    data = request.json
    table = 'donations' if data['type'] == 'donation' else 'food_requests'
    conn = get_db(); cursor = conn.cursor()
    # Using string formatting for table name is generally unsafe, but 'type' is controlled by our frontend JS.
    # For extra security in production, use an if/else block instead.
    if table == 'donations':
         cursor.execute("UPDATE donations SET status=%s WHERE id=%s", (data['status'], data['id']))
    else:
         cursor.execute("UPDATE food_requests SET status=%s WHERE id=%s", (data['status'], data['id']))
    conn.commit(); conn.close()
    return jsonify({"success": True, "message": "Status updated."})

# --- DASHBOARD & EXTRAS ---
@app.route('/api/stats', methods=['GET'])
def stats():
    conn = get_db(); cursor = conn.cursor()
    # Calculate total meals saved (accepted donations + accepted requests + event servings)
    cursor.execute("SELECT (SELECT COALESCE(SUM(quantity),0) FROM donations WHERE status='accepted') + (SELECT COALESCE(SUM(quantity),0) FROM food_requests WHERE status='accepted') + (SELECT COALESCE(SUM(servings),0) FROM event_donations)")
    total = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM donations WHERE status='pending'")
    p_don = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM food_requests WHERE status='pending'")
    p_req = cursor.fetchone()[0]
    conn.close()
    return jsonify({"meals": int(total), "p_don": p_don, "p_req": p_req})

@app.route('/api/activity', methods=['GET'])
def activity():
    conn = get_db(); cursor = conn.cursor(dictionary=True)
    # Combine both tables for a unified activity feed
    cursor.execute("""
        (SELECT 'Donation' as type, donor_name as name, quantity, location, status, created_at FROM donations WHERE status!='pending')
        UNION ALL
        (SELECT 'Request' as type, name, quantity, location, status, created_at FROM food_requests WHERE status!='pending')
        ORDER BY created_at DESC LIMIT 10
    """)
    data = cursor.fetchall(); conn.close()
    return jsonify(data)

# --- GENERIC POST HANDLERS (Events, Animals, Feedback) ---
@app.route('/api/event', methods=['POST'])
def event():
    d=request.json; conn=get_db(); c=conn.cursor()
    c.execute("INSERT INTO event_donations (organizer, contact, servings, location) VALUES (%s,%s,%s,%s)", (d['org'],d['contact'],d['qty'],d['loc']))
    conn.commit(); conn.close()
    return jsonify({"success":True, "message":"Event recorded."})

@app.route('/api/animal', methods=['POST'])
def animal():
    d=request.json; conn=get_db(); c=conn.cursor()
    c.execute("INSERT INTO animal_feed (source, quantity, location) VALUES (%s,%s,%s)", (d['src'],d['qty'],d['loc']))
    conn.commit(); conn.close()
    return jsonify({"success":True, "message":"Sent to shelters."})

@app.route('/api/feedback', methods=['POST'])
def feedback():
    d=request.json; conn=get_db(); c=conn.cursor()
    c.execute("INSERT INTO feedback (name, email, message) VALUES (%s,%s,%s)", (d['name'],d['email'],d['msg']))
    conn.commit(); conn.close()
    return jsonify({"success":True, "message":"Feedback sent."})

# --- SERVE FRONTEND ---
@app.route('/')
def index(): return send_from_directory('.', 'index.html')
@app.route('/<path:path>')
def static_file(path): return send_from_directory('.', path)

if __name__ == '__main__':
    # host='0.0.0.0' makes it accessible on the same Wi-Fi network
    app.run(host='0.0.0.0', port=5000, debug=True)