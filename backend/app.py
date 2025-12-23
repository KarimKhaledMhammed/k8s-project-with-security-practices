from flask import Flask, request, jsonify
import psycopg2, redis, os

app = Flask(__name__)

# --- CONFIGURATION ---
# We use environment variables so we can change these in Kubernetes without touching code
DB_HOST = os.getenv('DB_HOST', 'postgres.data-ns.svc.cluster.local')
DB_USER = "postgres"
DB_PASS = os.getenv('DB_PASS', 'securepass')
DB_NAME = "postgres"

REDIS_HOST = os.getenv('REDIS_HOST', 'redis.data-ns.svc.cluster.local')
REDIS_PASS = os.getenv('REDIS_PASS', 'securepass')

# --- CONNECT TO REDIS ---
try:
    r = redis.Redis(host=REDIS_HOST, port=6379, password=REDIS_PASS)
    r.ping() # Check connection
    print(f"Connected to Redis at {REDIS_HOST}")
except Exception as e:
    print(f"Failed to connect to Redis: {e}")

# --- HELPER: GET DB CONNECTION ---
def get_db_connection():
    return psycopg2.connect(host=DB_HOST, user=DB_USER, password=DB_PASS, dbname=DB_NAME)

# --- INITIALIZE DATABASE (Create Table) ---
def init_db():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, username VARCHAR(50) UNIQUE, password VARCHAR(50));")
        conn.commit()
        cur.close()
        conn.close()
        print("Database initialized successfully.")
    except Exception as e:
        print(f"DB Init Error: {e}")

# Initialize on startup
init_db()

@app.route('/')
def hello():
    return "Backend is Running!"

@app.route('/api/signup', methods=['POST'])
def signup():
    user = request.form['username']
    pw = request.form['password'] # We need password to save to DB
    
    try:
        # 1. Save to Postgres
        conn = get_db_connection()
        cur = conn.cursor()
        # Simple insert
        cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (user, pw))
        conn.commit()
        cur.close()
        conn.close()
        
        # 2. Cache in Redis
        r.set(user, "active") 
        
        return f"User {user} Signed Up! (Saved to DB in data-ns & Redis)"
    except Exception as e:
        return f"Error: {str(e)}", 500

@app.route('/api/signin', methods=['POST'])
def signin():
    user = request.form['username']
    pw = request.form['password']
    
    # Check Postgres
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM users WHERE username = %s AND password = %s", (user, pw))
        account = cur.fetchone()
        cur.close()
        conn.close()

        if account:
            return f"Welcome back, {user}!"
        else:
            return "Invalid credentials."
    except Exception as e:
        return f"Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)