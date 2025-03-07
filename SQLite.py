import sqlite3
from sqlite3 import Error


def create_connection():
    """Create a database connection to a SQLite database"""
    conn = None
    try:
        conn = sqlite3.connect('video_recommendations.db')
        return conn
    except Error as e:
        print(e)
    
    return conn

def create_tables(conn):
    """Create the necessary tables if they don't exist"""
    try:
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute()
        
        # Create video preferences table with foreign key to users
        cursor.execute()
        
        conn.commit()
    except Error as e:
        print(e)

# Add these functions to your existing FastAPI app
def store_new_user(name):
    """Store a new user and return the user ID"""
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

#Store a user's video preference
def store_video_preference(user_id, video_id, video_title):
   
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO video_preferences (user_id, video_id, video_title) VALUES (?, ?, ?)",
        (user_id, video_id, video_title)
    )
    conn.commit()
    conn.close()

#Get a user's video preferences
def get_user_preferences(user_id):
    
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT video_id, video_title FROM video_preferences WHERE user_id = ?",
        (user_id,)
    )
    preferences = cursor.fetchall()
    conn.close()
    return preferences

# Initialize the database when the app starts
def init_db():
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
    else:
        print("Error! Cannot create the database connection.")