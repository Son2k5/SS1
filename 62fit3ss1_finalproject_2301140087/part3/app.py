from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)

DATABASE = 'booklist3.db'


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row  
    return conn


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
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
        sample_books = [
            ('Fiction', 'To Kill a Mockingbird', 'Harper Lee', 2007, 'J.B. Lippincott & Co.'),
            ('Fiction', 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 2014, 'Harper'),
            ('Fiction', '1984', 'George Orwell', 2000, 'Secker & Warburg')
        ]
        
        cursor.executemany("""
            INSERT INTO book (genre, title, author, year, publisher)
            VALUES (?, ?, ?, ?, ?)
        """, sample_books)
        conn.commit()
        print("Database initialized with sample data.")
    
    conn.close()
    print("Database setup completed successfully.")



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create', methods=['POST'])
def create_book_web():
    genre = request.form.get('genre')
    title = request.form.get('title')
    author = request.form.get('author')
    year = int(request.form.get('year'))
    publisher = request.form.get('publisher')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO book (genre, title, author, year, publisher)
        VALUES (?, ?, ?, ?, ?)
    """, (genre, title, author, year, publisher))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_book_web():
    """Cập nhật sách qua web form"""
    book_id = int(request.form.get('id'))
    genre = request.form.get('genre')
    title = request.form.get('title')
    author = request.form.get('author')
    year = int(request.form.get('year'))
    publisher = request.form.get('publisher')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE book 
        SET genre = ?, title = ?, author = ?, year = ?, publisher = ?
        WHERE id = ?
    """, (genre, title, author, year, publisher, book_id))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_book_web():
    book_id = int(request.form.get('id'))
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))



@app.route('/api/list', methods=['GET'])
def api_list_books():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM book ORDER BY id")
        books = cursor.fetchall()
        conn.close()
        
        book_list = [dict(book) for book in books]
        
        return jsonify(book_list), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/add', methods=['POST'])
def api_add_book():
    try:
        data = request.get_json()
        required_fields = ['genre', 'title', 'author', 'year', 'publisher']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        genre = data['genre']
        title = data['title']
        author = data['author']
        year = int(data['year'])
        publisher = data['publisher']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO book (genre, title, author, year, publisher)
            VALUES (?, ?, ?, ?, ?)
        """, (genre, title, author, year, publisher))
        
        conn.commit()
        book_id = cursor.lastrowid
        conn.close()
        
        return jsonify({
            'message': 'Book added successfully',
            'id': book_id
        }), 201
        
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/update', methods=['POST'])
def api_update_book():
    try:
        book_id = request.args.get('id')
        if not book_id:
            return jsonify({'error': 'Missing book ID in query parameter'}), 400
        
        book_id = int(book_id)
        
        data = request.get_json()
        
        required_fields = ['genre', 'title', 'author', 'year', 'publisher']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        genre = data['genre']
        title = data['title']
        author = data['author']
        year = int(data['year'])
        publisher = data['publisher']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM book WHERE id = ?", (book_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        
        cursor.execute("""
            UPDATE book 
            SET genre = ?, title = ?, author = ?, year = ?, publisher = ?
            WHERE id = ?
        """, (genre, title, author, year, publisher, book_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Book updated successfully',
            'id': book_id
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete', methods=['GET'])
def api_delete_book():
    try:
        book_id = request.args.get('id')
        if not book_id:
            return jsonify({'error': 'Missing book ID in query parameter'}), 400
        
        book_id = int(book_id)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM book WHERE id = ?", (book_id,))
        if not cursor.fetchone():
            conn.close()
            return jsonify({'error': 'Book not found'}), 404
        
        cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'message': 'Book deleted successfully',
            'id': book_id
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500



@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    init_db()   
    app.run(debug=True, port=5000)