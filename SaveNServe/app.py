# app.py
# Your Python backend server, updated for MySQL
# To run:
# 1. Make sure you have Flask & MySQL Connector:
#    pip install Flask mysql-connector-python
# 2. Run your MySQL schema SQL file to create the database and tables.
# 3. !! UPDATE the MYSQL_CONFIG variable below with your credentials. !!
# 4. Run this server: python app.py

import mysql.connector
from mysql.connector import errorcode
import json
from flask import Flask, request, jsonify, send_from_directory

app = Flask(__name__)

# --- !! IMPORTANT !! ---
# Update this dictionary with your MySQL database credentials
MYSQL_CONFIG = {
    'user': 'root',           # Your MySQL username
    'password': 'tiger',   # Your MySQL password
    'host': 'localhost',      # Database host (usually 127.0.0.1 or localhost)
    'database': 'savenserve_db' # The database name you created
}

# --- Database Helper Functions ---

def get_db():
    """Connect to the MySQL database."""
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        return conn
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        return None # Return None if connection fails

def row_to_dict(cursor, row):
    """Helper to convert a MySQL row (tuple) to a dictionary."""
    if not row:
        return None
    column_names = [desc[0] for desc in cursor.description]
    return dict(zip(column_names, row))

# --- API Endpoints ---

@app.route('/api/signup', methods=['POST'])
def signup():
    """Handle new user signup."""
    data = request.json
    username = data.get('username')
    
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    
    # CHECK FOR DUPLICATE USER
    # MySQL uses %s as the placeholder
    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    
    if existing_user:
        cursor.close()
        conn.close()
        # Return an error if user already exists
        return jsonify({"success": False, "message": "Username already exists."}), 409
    
    # If not a duplicate, insert new user
    # WARNING: Passwords should be HASHED in a real application!
    try:
        cursor.execute(
            "INSERT INTO users (name, username, password, role) VALUES (%s, %s, %s, %s)",
            (data.get('name'), username, data.get('password'), data.get('role'))
        )
        conn.commit()
        message = "Account created successfully."
        success = True
    except mysql.connector.Error as err:
        message = f"Database error: {err}"
        success = False
    
    cursor.close()
    conn.close()
    
    return jsonify({"success": success, "message": message})

@app.route('/api/login', methods=['POST'])
def login():
    """Handle user login."""
    data = request.json
    username = data.get('username')
    password = data.get('password')
    
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    
    # WARNING: In a real app, you would hash the provided password and
    # compare it to the hashed password in the database.
    cursor.execute(
        "SELECT * FROM users WHERE username = %s AND password = %s",
        (username, password)
    )
    user_row = cursor.fetchone()
    user_data = row_to_dict(cursor, user_row) # Convert row to dict
    
    cursor.close()
    conn.close()
    
    if user_data:
        # Successful login
        del user_data['password'] # Don't send password back
        return jsonify({"success": True, "message": "Login successful", "user": user_data})
    else:
        # Invalid credentials
        return jsonify({"success": False, "message": "Invalid credentials"}), 401

@app.route('/api/donate', methods=['POST'])
def donate():
    """Save a new food donation."""
    data = request.json
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO donations (donor_name, quantity, location) VALUES (%s, %s, %s)",
        (data.get('donor'), data.get('qty'), data.get('location'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Donation recorded."})

@app.route('/api/event-donate', methods=['POST'])
def event_donate():
    """Save a new event donation."""
    data = request.json
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO event_donations (organizer_name, contact_info, approx_servings, location) VALUES (%s, %s, %s, %s)",
        (data.get('organizer'), data.get('contact'), data.get('servings'), data.get('location'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Event donation noted."})

@app.route('/api/request-food', methods=['POST'])
def request_food():
    """Save a new food request."""
    data = request.json
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO food_requests (requestor_name, organization, quantity_needed, location) VALUES (%s, %s, %s, %s)",
        (data.get('name'), data.get('org'), data.get('qty'), data.get('location'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Request submitted."})

@app.route('/api/feed-animals', methods=['POST'])
def feed_animals():
    """Save a new animal feed donation."""
    data = request.json
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO animal_feed_donations (source_name, quantity, location) VALUES (%s, %s, %s)",
        (data.get('source'), data.get('qty'), data.get('location'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Animal feed request recorded."})

@app.route('/api/feedback', methods=['POST'])
def feedback():
    """Save feedback from awareness page."""
    data = request.json
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO feedback (name, email, message) VALUES (%s, %s, %s)",
        (data.get('name'), data.get('email'), data.get('msg'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Thanks — feedback saved."})

@app.route('/api/contact', methods=['POST'])
def contact():
    """Save message from contact page."""
    data = request.json
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO contacts (name, email, message) VALUES (%s, %s, %s)",
        (data.get('name'), data.get('email'), data.get('msg'))
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"success": True, "message": "Message saved."})

@app.route('/api/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """Get statistics for the dashboard."""
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    
    cursor.execute("SELECT SUM(quantity) FROM donations")
    meals_saved = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM donations")
    donations_count = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM food_requests")
    requests_count = cursor.fetchone()[0] or 0
    
    cursor.execute("SELECT COUNT(*) FROM event_donations")
    events_count = cursor.fetchone()[0] or 0
    
    cursor.close()
    conn.close()
    
    return jsonify({
        "mealsSaved": int(meals_saved), # Ensure it's a number
        "donationsCount": donations_count,
        "requestsCount": requests_count,
        "eventsCount": events_count
    })

@app.route('/api/recent-donations', methods=['GET'])
def recent_donations():
    """Get recent donations for dashboard list."""
    conn = get_db()
    if not conn:
        return jsonify({"success": False, "message": "Database connection error."}), 500
        
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT donor_name, quantity, location, created_at FROM donations ORDER BY created_at DESC LIMIT 10"
    )
    
    # Get column names from cursor description
    column_names = [desc[0] for desc in cursor.description]
    # Fetch all rows and create a list of dictionaries
    donations = [dict(zip(column_names, row)) for row in cursor.fetchall()]
    
    cursor.close()
    conn.close()
    
    # Convert datetime objects to strings for JSON serialization
    for donation in donations:
        if 'created_at' in donation and hasattr(donation['created_at'], 'isoformat'):
            donation['created_at'] = donation['created_at'].isoformat()

    return jsonify(donations)


# --- Static File Serving ---
# Serve the HTML, CSS, JS, and asset files

@app.route('/')
def serve_index():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def serve_static_files(path):
    # This serves all other files (e.g., login.html, styles.css, scripts/app.js)
    return send_from_directory('.', path)


if __name__ == '__main__':
    print("--- Save N Serve Backend Server (MySQL) ---")
    print("Serving on http://127.0.0.1:5000")
    print("Make sure your MySQL server is running and config is correct.")
    app.run(debug=True, port=5000)