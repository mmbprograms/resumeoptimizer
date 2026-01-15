"""
Database models and functions for Resume Optimizer Web App
"""
import sqlite3
import hashlib
import secrets
from datetime import datetime
from typing import Optional, List, Dict, Tuple
import json


class Database:
    """Handle all database operations"""

    def __init__(self, db_path: str = "resume_optimizer.db"):
        self.db_path = db_path
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database tables"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                resume_count INTEGER DEFAULT 0,
                resume_limit INTEGER DEFAULT 50
            )
        """)

        # User profiles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                full_name TEXT,
                email TEXT,
                phone TEXT,
                linkedin_url TEXT,
                location TEXT,
                education_json TEXT,
                skills_json TEXT,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Work experiences table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_experiences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                start_date TEXT NOT NULL,
                end_date TEXT,
                is_current BOOLEAN DEFAULT 0,
                display_order INTEGER DEFAULT 0,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Experience bullets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS experience_bullets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                work_experience_id INTEGER NOT NULL,
                bullet_text TEXT NOT NULL,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (work_experience_id) REFERENCES work_experiences(id)
            )
        """)

        # Target jobs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS target_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                company_name TEXT NOT NULL,
                job_title TEXT NOT NULL,
                job_url TEXT,
                job_description TEXT,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)

        # Generated resumes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                target_job_id INTEGER NOT NULL,
                generated_bullets_json TEXT,
                html_content TEXT,
                pdf_filename TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id),
                FOREIGN KEY (target_job_id) REFERENCES target_jobs(id)
            )
        """)

        conn.commit()
        conn.close()

    # User authentication methods
    def hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}${pwd_hash}"

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify password against hash"""
        try:
            salt, pwd_hash = password_hash.split('$')
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
        except:
            return False

    def create_user(self, username: str, password: str) -> Optional[int]:
        """Create new user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        try:
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                (username, password_hash)
            )
            user_id = cursor.lastrowid

            # Create empty profile
            cursor.execute(
                "INSERT INTO user_profiles (user_id) VALUES (?)",
                (user_id,)
            )

            conn.commit()
            return user_id
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def authenticate_user(self, username: str, password: str) -> Optional[int]:
        """Authenticate user and return user_id if successful"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, password_hash FROM users WHERE username = ?",
            (username,)
        )
        row = cursor.fetchone()
        conn.close()

        if row and self.verify_password(password, row['password_hash']):
            return row['id']
        return None

    def get_user_info(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT username, resume_count, resume_limit FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def increment_resume_count(self, user_id: int):
        """Increment user's resume count"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE users SET resume_count = resume_count + 1 WHERE id = ?",
            (user_id,)
        )
        conn.commit()
        conn.close()

    def can_generate_resume(self, user_id: int) -> bool:
        """Check if user can generate another resume"""
        user_info = self.get_user_info(user_id)
        if user_info:
            return user_info['resume_count'] < user_info['resume_limit']
        return False

    # Profile methods
    def update_profile(self, user_id: int, profile_data: Dict):
        """Update user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE user_profiles SET
                full_name = ?,
                email = ?,
                phone = ?,
                linkedin_url = ?,
                location = ?,
                education_json = ?,
                skills_json = ?
            WHERE user_id = ?
        """, (
            profile_data.get('full_name'),
            profile_data.get('email'),
            profile_data.get('phone'),
            profile_data.get('linkedin_url'),
            profile_data.get('location'),
            json.dumps(profile_data.get('education', [])),
            json.dumps(profile_data.get('skills', [])),
            user_id
        ))

        conn.commit()
        conn.close()

    def get_profile(self, user_id: int) -> Optional[Dict]:
        """Get user profile"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            profile = dict(row)
            profile['education'] = json.loads(profile['education_json']) if profile['education_json'] else []
            profile['skills'] = json.loads(profile['skills_json']) if profile['skills_json'] else []
            return profile
        return None

    # Work experience methods
    def add_work_experience(self, user_id: int, company: str, title: str,
                           start_date: str, end_date: Optional[str],
                           is_current: bool) -> int:
        """Add work experience"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Get max display_order
        cursor.execute(
            "SELECT MAX(display_order) FROM work_experiences WHERE user_id = ?",
            (user_id,)
        )
        max_order = cursor.fetchone()[0]
        display_order = (max_order or 0) + 1

        cursor.execute("""
            INSERT INTO work_experiences
            (user_id, company_name, job_title, start_date, end_date, is_current, display_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (user_id, company, title, start_date, end_date, is_current, display_order))

        exp_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return exp_id

    def get_work_experiences(self, user_id: int) -> List[Dict]:
        """Get all work experiences for user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM work_experiences
            WHERE user_id = ?
            ORDER BY display_order
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_work_experience(self, exp_id: int):
        """Delete work experience and all its bullets"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM experience_bullets WHERE work_experience_id = ?", (exp_id,))
        cursor.execute("DELETE FROM work_experiences WHERE id = ?", (exp_id,))

        conn.commit()
        conn.close()

    # Bullet methods
    def add_bullet(self, work_experience_id: int, bullet_text: str):
        """Add bullet to work experience"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO experience_bullets (work_experience_id, bullet_text)
            VALUES (?, ?)
        """, (work_experience_id, bullet_text))

        conn.commit()
        conn.close()

    def add_bullets_bulk(self, work_experience_id: int, bullets: List[str]):
        """Add multiple bullets at once"""
        conn = self.get_connection()
        cursor = conn.cursor()

        for bullet in bullets:
            if bullet.strip():
                cursor.execute("""
                    INSERT INTO experience_bullets (work_experience_id, bullet_text)
                    VALUES (?, ?)
                """, (work_experience_id, bullet.strip()))

        conn.commit()
        conn.close()

    def get_bullets(self, work_experience_id: int) -> List[Dict]:
        """Get all bullets for work experience"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM experience_bullets
            WHERE work_experience_id = ? AND is_active = 1
            ORDER BY id
        """, (work_experience_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def delete_bullet(self, bullet_id: int):
        """Delete bullet"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM experience_bullets WHERE id = ?", (bullet_id,))
        conn.commit()
        conn.close()

    def update_bullet(self, bullet_id: int, bullet_text: str):
        """Update bullet text"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE experience_bullets SET bullet_text = ? WHERE id = ?",
            (bullet_text, bullet_id)
        )
        conn.commit()
        conn.close()

    # Target job methods
    def add_target_job(self, user_id: int, company: str, title: str,
                      url: Optional[str], description: Optional[str]) -> int:
        """Add target job"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO target_jobs (user_id, company_name, job_title, job_url, job_description)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, company, title, url, description))

        job_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return job_id

    def get_target_jobs(self, user_id: int) -> List[Dict]:
        """Get all target jobs for user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM target_jobs
            WHERE user_id = ?
            ORDER BY date_added DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]

    def get_target_job(self, job_id: int) -> Optional[Dict]:
        """Get single target job"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM target_jobs WHERE id = ?", (job_id,))
        row = cursor.fetchone()
        conn.close()

        if row:
            return dict(row)
        return None

    def delete_target_job(self, job_id: int):
        """Delete target job"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM target_jobs WHERE id = ?", (job_id,))
        conn.commit()
        conn.close()

    def update_job_description(self, job_id: int, description: str):
        """Update job description"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE target_jobs SET job_description = ? WHERE id = ?",
            (description, job_id)
        )
        conn.commit()
        conn.close()

    # Resume methods
    def save_generated_resume(self, user_id: int, target_job_id: int,
                             bullets_json: str, html_content: str,
                             pdf_filename: str) -> int:
        """Save generated resume"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO generated_resumes
            (user_id, target_job_id, generated_bullets_json, html_content, pdf_filename)
            VALUES (?, ?, ?, ?, ?)
        """, (user_id, target_job_id, bullets_json, html_content, pdf_filename))

        resume_id = cursor.lastrowid
        conn.commit()
        conn.close()

        return resume_id

    def get_user_resumes(self, user_id: int) -> List[Dict]:
        """Get all generated resumes for user"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT gr.*, tj.company_name, tj.job_title
            FROM generated_resumes gr
            JOIN target_jobs tj ON gr.target_job_id = tj.id
            WHERE gr.user_id = ?
            ORDER BY gr.created_at DESC
        """, (user_id,))

        rows = cursor.fetchall()
        conn.close()

        return [dict(row) for row in rows]
