import os
import asyncpg
from config import DATABASE_URL
import datetime

class Database:
    def __init__(self):
        self.conn = None
    
    async def init_db(self):
        """Database initialization"""
        self.conn = await asyncpg.connect(DATABASE_URL)
        
        # Jadvalarni yaratish
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS user_settings (
                user_id BIGINT PRIMARY KEY,
                username VARCHAR(255),
                full_name VARCHAR(255),
                employee_name VARCHAR(255),
                region VARCHAR(100),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await self.conn.execute('''
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
        
        await self.conn.execute('''
            CREATE TABLE IF NOT EXISTS pozivnoy (
                id SERIAL PRIMARY KEY,
                user_id BIGINT,
                pozivnoy_number VARCHAR(20) NOT NULL,
                region VARCHAR(100),
                employee_name VARCHAR(255),
                created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    async def save_user_settings(self, user_id, username, full_name, employee_name=None, region=None):
        await self.conn.execute('''
            INSERT INTO user_settings (user_id, username, full_name, employee_name, region)
            VALUES ($1, $2, $3, $4, $5)
            ON CONFLICT (user_id) 
            DO UPDATE SET 
                username = EXCLUDED.username,
                full_name = EXCLUDED.full_name,
                employee_name = COALESCE(EXCLUDED.employee_name, user_settings.employee_name),
                region = COALESCE(EXCLUDED.region, user_settings.region)
        ''', user_id, username, full_name, employee_name, region)
    
    async def get_user_settings(self, user_id):
        result = await self.conn.fetchrow(
            'SELECT employee_name, region FROM user_settings WHERE user_id = $1',
            user_id
        )
        return (result['employee_name'], result['region']) if result else (None, None)
    
    async def save_number(self, user_id, phone, comment, region, employee_name):
        await self.conn.execute('''
            INSERT INTO numbers (user_id, phone, comment, region, employee_name)
            VALUES ($1, $2, $3, $4, $5)
        ''', user_id, phone, comment, region, employee_name)
    
    async def save_pozivnoy(self, user_id, pozivnoy_number, region, employee_name):
        await self.conn.execute('''
            INSERT INTO pozivnoy (user_id, pozivnoy_number, region, employee_name)
            VALUES ($1, $2, $3, $4)
        ''', user_id, pozivnoy_number, region, employee_name)
    
    async def get_today_numbers(self, user_id):
        return await self.conn.fetch('''
            SELECT phone, comment, region FROM numbers 
            WHERE user_id = $1 AND DATE(created_date) = CURRENT_DATE
            ORDER BY created_date
        ''', user_id)
    
    async def get_today_pozivnoy(self, user_id):
        return await self.conn.fetch('''
            SELECT pozivnoy_number, region FROM pozivnoy 
            WHERE user_id = $1 AND DATE(created_date) = CURRENT_DATE
            ORDER BY created_date
        ''', user_id)

# Global database instance
db = Database()