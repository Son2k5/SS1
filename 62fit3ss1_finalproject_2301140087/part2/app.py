from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  
    'password': '123456',  
    'database': 'bookList'
}


def get_db_connection():
    try:
        getConnection = mysql.connector.connect(**DB_CONFIG)
        return getConnection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def init_db():
    try:
        connectionValue = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connectionValue.cursor()
        
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS book (
                id INTEGER PRIMARY KEY AUTO_INCREMENT,
                genre TEXT NOT NULL,
                title TEXT NOT NULL,
                author TEXT NOT NULL,
                year INTEGER NOT NULL,
                publisher TEXT NOT NULL
            )
        """)
        
        cursor.execute("SELECT COUNT(*) FROM book")
        count = cursor.fetchone()[0]
        
        if count == 0:
            start_books = [
                ('Fiction', 'To Kill a Mockingbird', 'Harper Lee', 2007, 'J.B. Lippincott & Co.'),
                ('Fiction', 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 2014, 'Harper'),
                ('Fiction', '1984', 'George Orwell', 2000, 'Secker & Warburg')
            ]
            
            cursor.executemany("""
                INSERT INTO book (genre, title, author, year, publisher)
                VALUES (%s, %s, %s, %s, %s)
            """, start_books)
            connectionValue.commit()
            print("Database initialized with sample data.")
        
        cursor.close()
        connectionValue.close()
        print("Database setup completed successfully.")
        
    except Error as e:
        print(f"Error initializing database: {e}")


@app.route('/')
def index():
    getConnection = get_db_connection()
    if not getConnection:
        return "Database connection error", 500
    
    cursor = getConnection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book ORDER BY id")
    books = cursor.fetchall()
    
    cursor.close()
    getConnection.close()
    
    return render_template('index.html', bookList=books)


@app.route('/create', methods=['POST'])
def create_book():
    genre = request.form.get('genre')
    title = request.form.get('title')
    author = request.form.get('author')
    year = int(request.form.get('year'))
    publisher = request.form.get('publisher')
    
    getConnection = get_db_connection()
    if not getConnection:
        return "Database connection error", 500
    
    cursor = getConnection.cursor()
    cursor.execute("""
        INSERT INTO book (genre, title, author, year, publisher)
        VALUES (%s, %s, %s, %s, %s)
    """, (genre, title, author, year, publisher))
    
    getConnection.commit()
    cursor.close()
    getConnection.close()
    
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_book():
    book_id = int(request.form.get('id'))
    genre = request.form.get('genre')
    title = request.form.get('title')
    author = request.form.get('author')
    year = int(request.form.get('year'))
    publisher = request.form.get('publisher')
    
    getConnection = get_db_connection()
    if not getConnection:
        return "Database connection error", 500
    
    cursor = getConnection.cursor()
    cursor.execute("""
        UPDATE book 
        SET genre = %s, title = %s, author = %s, year = %s, publisher = %s
        WHERE id = %s
    """, (genre, title, author, year, publisher, book_id))
    
    getConnection.commit()
    cursor.close()
    getConnection.close()
    
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_book():
    book_id = int(request.form.get('id'))
    
    getConnection = get_db_connection()
    if not getConnection:
        return "Database connection error", 500
    
    cursor = getConnection.cursor()
    cursor.execute("DELETE FROM book WHERE id = %s", (book_id,))
    
    getConnection.commit()
    cursor.close()
    getConnection.close()
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)