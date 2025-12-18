from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


bookList = [
    {'id': 1, 'genre': 'Fiction', 'title': 'To Kill a Mockingbird', 'author': 'Harper Lee',
     'year': 2007, 'publisher': 'J.B. Lippincott & Co.'},
    {'id': 2, 'genre': 'Fiction', 'title': 'Sapiens: A Brief History of Humankind', 'author':
     'Yuval Noah Harari', 'year': 2014, 'publisher': 'Harper'},
    {'id': 3, 'genre': 'Fiction', 'title': '1984', 'author': 'George Orwell', 'year': 2000,
     'publisher': 'Secker & Warburg'}
]

NextIDValue= 4


@app.route('/')
def index():
    return render_template('index.html', bookList=bookList)


@app.route('/create', methods=['POST'])
def create_book():
    global NextIDValue
    
    new_book_value = {
        'id': NextIDValue,
        'genre': request.form.get('genre'),
        'title': request.form.get('title'),
        'author': request.form.get('author'),
        'year': int(request.form.get('year')),
        'publisher': request.form.get('publisher')
    }
    bookList.append(new_book_value)
    NextIDValue += 1
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_book():
    book_id_value = int(request.form.get('id'))

    bookValue = None
    for book in bookList:
        if book['id'] == book_id_value:
            bookValue = book
            break

    if bookValue is not None:
        bookValue['genre'] = request.form.get('genre')
        bookValue['title'] = request.form.get('title')
        bookValue['author'] = request.form.get('author')
        bookValue['year'] = int(request.form.get('year'))
        bookValue['publisher'] = request.form.get('publisher')

    return redirect(url_for('index'))



@app.route('/delete', methods=['POST'])
def delete_book():
    book_id = int(request.form.get('id'))

    for book in bookList:
        if book['id'] == book_id:
            bookList.remove(book)
            break

    return redirect(url_for('index'))



if __name__ == '__main__':
    app.run(debug=True)