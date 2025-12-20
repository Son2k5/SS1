from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os

app = Flask(__name__)


DATABASE = 'booklist3.db'


def get_db_getConnectionection():
    getConnection = sqlite3.connect(DATABASE)
    getConnection.row_factory = sqlite3.Row  
    return getConnection


def init_db():
    getConnection = get_db_getConnectionection()
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
        sample_books = [
            ('Fiction', 'To Kill a Mockingbird', 'Harper Lee', 2007, 'J.B. Lippincott & Co.'),
            ('Fiction', 'Sapiens: A Brief History of Humankind', 'Yuval Noah Harari', 2014, 'Harper'),
            ('Fiction', '1984', 'George Orwell', 2000, 'Secker & Warburg')
        ]
        
        cursor.executemany("""
            INSERT INTO book (genre, title, author, year, publisher)
            VALUES (?, ?, ?, ?, ?)
        """, sample_books)
        getConnection.commit()
        print("Database initialized with sample data.")
    
    getConnection.close()
    print("Database setup completed successfully.")




@app.route('/')
def index():
    return render_template('index.html')


@app.route('/create', methods=['POST'])
def create_book_web():
    genreValue = request.form.get('genre')
    titleValue = request.form.get('title')
    authorValue = request.form.get('author')
    yearValue = int(request.form.get('year'))
    publisherValue = request.form.get('publisher')
    
    getConnection = get_db_getConnectionection()
    cursor = getConnection.cursor()
    cursor.execute("""
        INSERT INTO book (genre, title, author, year, publisher)
        VALUES (?, ?, ?, ?, ?)
    """, (genreValue, titleValue, authorValue, yearValue, publisherValue))
    
    getConnection.commit()
    getConnection.close()
    
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_book_web():
    book_id_value = int(request.form.get('id'))
    genreValue = request.form.get('genre')
    titleValue = request.form.get('title')
    authorValue = request.form.get('author')
    yearValue = int(request.form.get('year'))
    publisherValue = request.form.get('publisher')
    
    getConnection = get_db_getConnectionection()
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
def delete_book_web():
    selected_id_values = request.form.getlist('ids')
    
    if selected_id_values:
        getConnection = get_db_getConnectionection()
        cursor = getConnection.cursor()
        
        placeholders = ','.join('?' * len(selected_id_values))
        query = f"DELETE FROM book WHERE id IN ({placeholders})"
        cursor.execute(query, selected_id_values)
        
        getConnection.commit()
        getConnection.close()
    
    return redirect(url_for('index'))



@app.route('/api/list', methods=['GET'])
def api_list_books():
    try:
        getConnection = get_db_getConnectionection()
        cursor = getConnection.cursor()
        cursor.execute("SELECT * FROM book ORDER BY id")
        books = cursor.fetchall()
        getConnection.close()
        
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
        
        getConnection = get_db_getConnectionection()
        cursor = getConnection.cursor()
        cursor.execute("""
            INSERT INTO book (genre, title, author, year, publisher)
            VALUES (?, ?, ?, ?, ?)
        """, (genre, title, author, year, publisher))
        
        getConnection.commit()
        book_id = cursor.lastrowid
        getConnection.close()
        
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
        
        genreValue = data['genre']
        titleValue = data['title']
        authorValue = data['author']
        yearValue = int(data['year'])
        publisherValue = data['publisher']
        
        getConnection = get_db_getConnectionection()
        cursor = getConnection.cursor()
        
        cursor.execute("SELECT id FROM book WHERE id = ?", (book_id,))
        if not cursor.fetchone():
            getConnection.close()
            return jsonify({'error': 'Book not found'}), 404
        
        cursor.execute("""
            UPDATE book 
            SET genre = ?, title = ?, author = ?, year = ?, publisher = ?
            WHERE id = ?
        """, (genreValue, titleValue, authorValue, yearValue, publisherValue, book_id))
        
        getConnection.commit()
        getConnection.close()
        
        return jsonify({
            'message': 'Book updated successfully',
            'id': book_id
        }), 200
        
    except ValueError as e:
        return jsonify({'error': 'Invalid data format'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/delete', methods=['GET', 'POST'])
def api_delete_book():
    try:
        getConnection = get_db_getConnectionection()
        cursor = getConnection.cursor()
        
        if request.method == 'GET':
            book_id = request.args.get('id')
            if not book_id:
                return jsonify({'error': 'Missing book ID in query parameter'}), 400
            
            book_id = int(book_id)
            
            cursor.execute("SELECT id FROM book WHERE id = ?", (book_id,))
            if not cursor.fetchone():
                getConnection.close()
                return jsonify({'error': 'Book not found'}), 404
            
            cursor.execute("DELETE FROM book WHERE id = ?", (book_id,))
            getConnection.commit()
            getConnection.close()
            
            return jsonify({
                'message': 'Book deleted successfully',
                'id': book_id
            }), 200
            
        else: 
            data = request.get_json()
            
            if 'ids' not in data or not isinstance(data['ids'], list):
                return jsonify({'error': 'Missing or invalid "ids" field in request body'}), 400
            
            ids_to_delete = [int(id) for id in data['ids']]
            
            if not ids_to_delete:
                return jsonify({'error': 'No IDs provided'}), 400
            
            placeholders = ','.join('?' * len(ids_to_delete))
            cursor.execute(f"SELECT id FROM book WHERE id IN ({placeholders})", ids_to_delete)
            existing_ids = [row[0] for row in cursor.fetchall()]
            
            if not existing_ids:
                getConnection.close()
                return jsonify({'error': 'No books found with provided IDs'}), 404
            
            cursor.execute(f"DELETE FROM book WHERE id IN ({placeholders})", ids_to_delete)
            getConnection.commit()
            getConnection.close()
            
            return jsonify({
                'message': f'{len(existing_ids)} book(s) deleted successfully',
                'deleted_ids': existing_ids
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