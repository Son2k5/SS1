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

next_id_Value = 4


@app.route('/')
def index():
    return render_template('index.html', bookList=bookList)


@app.route('/create', methods=['POST'])
def create_book():
    global next_id_Value
    
    new_book_value = {
        'id': next_id_Value,
        'genre': request.form.get('genre'),
        'title': request.form.get('title'),
        'author': request.form.get('author'),
        'year': int(request.form.get('year')),
        'publisher': request.form.get('publisher')
    }
    bookList.append(new_book_value)
    next_id_Value += 1
    return redirect(url_for('index'))


@app.route('/update', methods=['POST'])
def update_book():
    book_id = int(request.form['id'])

    for book in bookList:
        if book['id'] == book_id:
            book['genre'] = request.form['genre']
            book['title'] = request.form['title']
            book['author'] = request.form['author']
            book['year'] = int(request.form['year'])
            book['publisher'] = request.form['publisher']
            break

    return redirect(url_for('index'))



@app.route('/delete', methods=['POST'])
def delete_book():
    global bookList
    selected_id_Values = request.form.getlist('ids')
    if selected_id_Values:
        ids_to_delete = [int(id) for id in selected_id_Values]
        bookList = [b for b in bookList if b['id'] not in ids_to_delete]
    
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)