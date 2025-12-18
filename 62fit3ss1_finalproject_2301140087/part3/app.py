from flask import Flask, render_template, request, redirect, url_for, jsonify
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',  
    'password': '123456',  
    'database': 'booklist_db'
}


def get_db_connection():
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def init_db():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        cursor = connection.cursor()
        
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
            sample_books = [
                ('Fiction', 'To Kill a Mockingbird', 'Harper Lee', 2007, 'J.B. Lippincott & Co.'),
                ('Fiction', 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 2014, 'Harper'),
                ('Fiction', '1984', 'George Orwell', 2000, 'Secker & Warburg')
            ]
            
            cursor.executemany("""
                INSERT INTO book (genre, title, author, year, publisher)
                VALUES (%s, %s, %s, %s, %s)
            """, sample_books)
            connection.commit()
            print("Database initialized with sample data.")
        
        cursor.close()
        connection.close()
        print("Database setup completed successfully.")
        
    except Error as e:
        print(f"Error initializing database: {e}")



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
    
    connection = get_db_connection()
    if not connection:
        return "Database connection error", 500
    
    cursor = connection.cursor()
    cursor.execute("""
        INSERT INTO book (genre, title, author, year, publisher)
        VALUES (%s, %s, %s, %s, %s)
    """, (genre, title, author, year, publisher))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_book_web():
    book_id = int(request.form.get('id'))
    genre = request.form.get('genre')
    title = request.form.get('title')
    author = request.form.get('author')
    year = int(request.form.get('year'))
    publisher = request.form.get('publisher')
    
    connection = get_db_connection()
    if not connection:
        return "Database connection error", 500
    
    cursor = connection.cursor()
    cursor.execute("""
        UPDATE book 
        SET genre = %s, title = %s, author = %s, year = %s, publisher = %s
        WHERE id = %s
    """, (genre, title, author, year, publisher, book_id))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_book_web():
    book_id = int(request.form.get('id'))
    
    connection = get_db_connection()
    if not connection:
        return "Database connection error", 500
    
    cursor = connection.cursor()
    cursor.execute("DELETE FROM book WHERE id = %s", (book_id,))
    
    connection.commit()
    cursor.close()
    connection.close()
    
    return redirect(url_for('index'))



@app.route('/api/list', methods=['GET'])
def api_list_books():
    connection = get_db_connection()
    if not connection:
        return jsonify({'error': 'Database connection error'}), 500
    
    cursor = connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM book ORDER BY id")
    books = cursor.fetchall()
    
    cursor.close()
    connection.close()
    
    return jsonify(books), 200


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
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection error'}), 500
        
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO book (genre, title, author, year, publisher)
            VALUES (%s, %s, %s, %s, %s)
        """, (genre, title, author, year, publisher))
        
        connection.commit()
        book_id = cursor.lastrowid
        
        cursor.close()
        connection.close()
        
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
        # Lấy ID từ query parameter
        book_id = request.args.get('id')
        if not book_id:
            return jsonify({'error': 'Missing book ID in query parameter'}), 400
        
        book_id = int(book_id)
        
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['genre', 'title', 'author', 'year', 'publisher']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        genre = data['genre']
        title = data['title']
        author = data['author']
        year = int(data['year'])
        publisher = data['publisher']
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection error'}), 500
        
        cursor = connection.cursor()
        
        # Kiểm tra xem sách có tồn tại không
        cursor.execute("SELECT id FROM book WHERE id = %s", (book_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': 'Book not found'}), 404
        
        # Update book
        cursor.execute("""
            UPDATE book 
            SET genre = %s, title = %s, author = %s, year = %s, publisher = %s
            WHERE id = %s
        """, (genre, title, author, year, publisher, book_id))
        
        connection.commit()
        cursor.close()
        connection.close()
        
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
        # Lấy ID từ query parameter
        book_id = request.args.get('id')
        if not book_id:
            return jsonify({'error': 'Missing book ID in query parameter'}), 400
        
        book_id = int(book_id)
        
        connection = get_db_connection()
        if not connection:
            return jsonify({'error': 'Database connection error'}), 500
        
        cursor = connection.cursor()
        
        # Kiểm tra xem sách có tồn tại không
        cursor.execute("SELECT id FROM book WHERE id = %s", (book_id,))
        if not cursor.fetchone():
            cursor.close()
            connection.close()
            return jsonify({'error': 'Book not found'}), 404
        
        # Delete book
        cursor.execute("DELETE FROM book WHERE id = %s", (book_id,))
        
        connection.commit()
        cursor.close()
        connection.close()
        
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
    # Khởi tạo database khi chạy app
    init_db()
    app.run(debug=True, port=5000)