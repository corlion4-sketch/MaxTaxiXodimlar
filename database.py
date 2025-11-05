import psycopg2
from contextlib import contextmanager
from config import DATABASE_URL
import datetime

class Database:
    def __init__(self):
        self.init_db()
    
    @contextmanager
    def get_connection(self):
        conn = psycopg2.connect(DATABASE_URL)
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def init_db(self):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                # Foydalanuvchi sozlamalari jadvali
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS user_settings (
                        user_id BIGINT PRIMARY KEY,
                        username VARCHAR(255),
                        full_name VARCHAR(255),
                        employee_name VARCHAR(255),
                        region VARCHAR(100),
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Raqamlar jadvali
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS numbers (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        phone VARCHAR(20) NOT NULL,
                        comment TEXT,
                        region VARCHAR(100),
                        employee_name VARCHAR(255),
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # Pozivnoylar jadvali
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS pozivnoy (
                        id SERIAL PRIMARY KEY,
                        user_id BIGINT,
                        pozivnoy_number VARCHAR(20) NOT NULL,
                        region VARCHAR(100),
                        employee_name VARCHAR(255),
                        created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
    
    def save_user_settings(self, user_id, username, full_name, employee_name=None, region=None):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO user_settings (user_id, username, full_name, employee_name, region)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (user_id) 
                    DO UPDATE SET 
                        username = EXCLUDED.username,
                        full_name = EXCLUDED.full_name,
                        employee_name = COALESCE(EXCLUDED.employee_name, user_settings.employee_name),
                        region = COALESCE(EXCLUDED.region, user_settings.region)
                ''', (user_id, username, full_name, employee_name, region))
    
    def get_user_settings(self, user_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT employee_name, region FROM user_settings WHERE user_id = %s
                ''', (user_id,))
                result = cur.fetchone()
                return result if result else (None, None)
    
    def save_number(self, user_id, phone, comment, region, employee_name):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO numbers (user_id, phone, comment, region, employee_name)
                    VALUES (%s, %s, %s, %s, %s)
                ''', (user_id, phone, comment, region, employee_name))
    
    def save_pozivnoy(self, user_id, pozivnoy_number, region, employee_name):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO pozivnoy (user_id, pozivnoy_number, region, employee_name)
                    VALUES (%s, %s, %s, %s)
                ''', (user_id, pozivnoy_number, region, employee_name))
    
    def get_today_numbers(self, user_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT phone, comment, region FROM numbers 
                    WHERE user_id = %s AND DATE(created_date) = CURRENT_DATE
                    ORDER BY created_date
                ''', (user_id,))
                return cur.fetchall()
    
    def get_today_pozivnoy(self, user_id):
        with self.get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT pozivnoy_number, region FROM pozivnoy 
                    WHERE user_id = %s AND DATE(created_date) = CURRENT_DATE
                    ORDER BY created_date
                ''', (user_id,))
                return cur.fetchall()

db = Database()