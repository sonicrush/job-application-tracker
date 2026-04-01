import mysql.connector
from mysql.connector import Error
import json
import os
from dotenv import load_dotenv

load_dotenv()

def get_db():
    """Get database connection"""
    try:
        conn = mysql.connector.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            user=os.getenv('DB_USER', 'root'),
            password=os.getenv('DATABASE_PASSWORD', ''),
            database=os.getenv('DB_NAME', 'job_tracker')
        )
        return conn
    except Error as e:
        print(f"Error connecting to database: {e}")
        return None

def init_db():
    """Initialize database tables"""
    conn = get_db()
    if conn is None:
        return False

    cursor = conn.cursor()

    try:
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                company_id INT PRIMARY KEY AUTO_INCREMENT,
                company_name VARCHAR(100) NOT NULL,
                industry VARCHAR(50),
                website VARCHAR(200),
                city VARCHAR(50),
                state VARCHAR(50),
                notes TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jobs (
                job_id INT PRIMARY KEY AUTO_INCREMENT,
                company_id INT,
                job_title VARCHAR(100) NOT NULL,
                job_type ENUM('Full-time','Part-time','Contract','Internship'),
                salary_min INT,
                salary_max INT,
                job_url VARCHAR(300),
                date_posted DATE,
                requirements JSON,
                FOREIGN KEY (company_id) REFERENCES companies(company_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                application_id INT PRIMARY KEY AUTO_INCREMENT,
                job_id INT,
                application_date DATE NOT NULL,
                status ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn'),
                resume_version VARCHAR(50),
                cover_letter_sent BOOLEAN,
                interview_data JSON,
                FOREIGN KEY (job_id) REFERENCES jobs(job_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                contact_id INT PRIMARY KEY AUTO_INCREMENT,
                company_id INT,
                contact_name VARCHAR(100) NOT NULL,
                title VARCHAR(100),
                email VARCHAR(100),
                phone VARCHAR(20),
                linkedin_url VARCHAR(200),
                notes TEXT,
                FOREIGN KEY (company_id) REFERENCES companies(company_id)
            )
        ''')

        conn.commit()
        print("Database initialized successfully")
        return True
    except Error as e:
        print(f"Error initializing database: {e}")
        return False
    finally:
        cursor.close()
        conn.close()
