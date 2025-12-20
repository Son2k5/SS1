from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'booklist2.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  
    return conn


def init_db():
    getConnection = get_db_connection()
    cursor = getConnection.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
        sample_book_values = [
            ('Fiction', 'To Kill a Mockingbird', 'Harper Lee', 2007, 'J.B. Lippincott & Co.'),
            ('Fiction', 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 2014, 'Harper'),
            ('Fiction', '1984', 'George Orwell', 2000, 'Secker & Warburg')
        ]
        
        cursor.executemany("""
            INSERT INTO book (genre, title, author, year, publisher)
            VALUES (?, ?, ?, ?, ?)
        """, sample_book_values)
        getConnection.commit()
        print("Database initialized with sample data.")
    
    getConnection.close()
    print("Database setup completed successfully.")


@app.route('/')
def index():
    getConnection = get_db_connection()
    cursor = getConnection.cursor()
    cursor.execute("SELECT * FROM book ORDER BY id")
    books = cursor.fetchall()
    getConnection.close()
    
    book_list_value = [dict(book) for book in books]
    
    return render_template('index.html', bookList=book_list_value)


@app.route('/create', methods=['POST'])
def create_book():
    genreValue = request.form.get('genre')
    titleValue = request.form.get('title')
    authorValue = request.form.get('author')
    yearValue = int(request.form.get('year'))
    publisherValue = request.form.get('publisher')
    
    getConnection = get_db_connection()
    cursor = getConnection.cursor()
    cursor.execute("""
        INSERT INTO book (genre, title, author, year, publisher)
        VALUES (?, ?, ?, ?, ?)
    """, (genreValue, titleValue, authorValue, yearValue, publisherValue))
    
    getConnection.commit()
    getConnection.close()
    
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_book():
    book_id_value = int(request.form.get('id'))
    genreValue = request.form.get('genre')
    titleValue = request.form.get('title')
    authorValue = request.form.get('author')
    yearValue = int(request.form.get('year'))
    publisherValue = request.form.get('publisher')
    
    getConnection = get_db_connection()
    cursor = getConnection.cursor()
    cursor.execute("""
        UPDATE book 
        SET genre = ?, title = ?, author = ?, year = ?, publisher = ?
        WHERE id = ?
    """, (genreValue, titleValue, authorValue, yearValue, publisherValue, book_id_value))
    
    getConnection.commit()
    getConnection.close()
    
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_book():
    selected_id_values = request.form.getlist('ids')
    
    if selected_id_values:
        getConnection = get_db_connection()
        cursor = getConnection.cursor()
        
        placeholders = ','.join('?' * len(selected_id_values))
        query = f"DELETE FROM book WHERE id IN ({placeholders})"
        cursor.execute(query, selected_id_values)
        
        getConnection.commit()
        getConnection.close()
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    init_db()
    app.run(debug=True)