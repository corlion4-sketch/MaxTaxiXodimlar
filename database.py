import sqlite3
import os

class Database:
    def __init__(self):
        self.db_path = "/tmp/bot_database.db"
        self.init_db()
    
    def get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    def init_db(self):
        conn = self.get_connection()
        cur = conn.cursor()
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                employee_name TEXT,
                region TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS numbers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                phone TEXT NOT NULL,
                comment TEXT,
                region TEXT,
                employee_name TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        cur.execute('''
            CREATE TABLE IF NOT EXISTS pozivnoy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                pozivnoy_number TEXT NOT NULL,
                region TEXT,
                employee_name TEXT,
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_user_settings(self, user_id, username, full_name, employee_name=None, region=None):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT OR REPLACE INTO user_settings 
            (user_id, username, full_name, employee_name, region)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, employee_name, region))
        conn.commit()
        conn.close()
    
    def get_user_settings(self, user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('SELECT employee_name, region FROM user_settings WHERE user_id = ?', (user_id,))
        result = cur.fetchone()
        conn.close()
        if result:
            return (result['employee_name'], result['region'])
        return (None, None)
    
    def save_number(self, user_id, phone, comment, region, employee_name):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO numbers (user_id, phone, comment, region, employee_name)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, phone, comment, region, employee_name))
        conn.commit()
        conn.close()
    
    def save_pozivnoy(self, user_id, pozivnoy_number, region, employee_name):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO pozivnoy (user_id, pozivnoy_number, region, employee_name)
            VALUES (?, ?, ?, ?)
        ''', (user_id, pozivnoy_number, region, employee_name))
        conn.commit()
        conn.close()
    
    def get_today_numbers(self, user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT phone, comment, region FROM numbers 
            WHERE user_id = ? AND DATE(created_date) = DATE('now')
            ORDER BY created_date
        ''', (user_id,))
        results = cur.fetchall()
        conn.close()
        return [(row['phone'], row['comment'], row['region']) for row in results]
    
    def get_today_pozivnoy(self, user_id):
        conn = self.get_connection()
        cur = conn.cursor()
        cur.execute('''
            SELECT pozivnoy_number, region FROM pozivnoy 
            WHERE user_id = ? AND DATE(created_date) = DATE('now')
            ORDER BY created_date
        ''', (user_id,))
        results = cur.fetchall()
        conn.close()
        return [(row['pozivnoy_number'], row['region']) for row in results]

db = Database()
