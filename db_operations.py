import sqlite3

def initialize_db():
    # Connect to users database and create table if it doesn't exist
    conn_users = sqlite3.connect("users.db")
    cursor_users = conn_users.cursor()
    cursor_users.execute("""
    CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT,
    last_name TEXT
    )
    """)
    conn_users.commit()

    # Seed the users table with predefined users
    users = [
        ("Godric", "Gryffindor"),
        ("Helga", "Hufflepuff"),
        ("Rowena", "Ravenclaw"),
        ("Salazar", "Slytherin"),
        ("Luna", "Lovegood")
    ]
    
    cursor_users.executemany("INSERT OR IGNORE INTO users (first_name, last_name) VALUES (?, ?)", users)
    conn_users.commit()
    conn_users.close()

    # Connect to habits database and create table if it doesn't exist
    conn_habits = sqlite3.connect("habits.db")
    cursor_habits = conn_habits.cursor()
    cursor_habits.execute("""
    CREATE TABLE IF NOT EXISTS habits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        name TEXT,
        frequency TEXT,
        created_date TEXT,
        last_completed_date TEXT,
        current_streak INTEGER,
        longest_streak INTEGER,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    """)
    conn_habits.commit()
    conn_habits.close()
