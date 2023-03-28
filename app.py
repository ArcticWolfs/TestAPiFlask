import datetime
import os
from encodings.utf_8 import decode
from functools import wraps

import jwt
import psycopg2
from flask import Flask, jsonify, request, make_response

app = Flask(__name__)
url = os.environ.get("DATABASE_URL")  # gets variables from environment
secret_key = os.environ.get("SECRET_KEY")
connection = psycopg2.connect(url)


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing'}), 401
        try:
            data = jwt.decode(token, os.environ.get("SECRET_KEY"), algorithms=["HS256"])
        except:
            return jsonify({'message': "Token is invalid"}), 401

        return f(*args, **kwargs)

    return decorated


@app.route('/')
def hello_world():  # put application's code here
    return 'Hello World!'


@app.post('/book')
def book():
    data = request.get_json()
    title = data['title']
    price = data['price']
    description = data['description']
    author_id = data['author_id']

    with connection:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO book (title, price, description, author_id) VALUES (%s, %s, %s, %s);",
                           (title, price, description, author_id))
    return 'Data added'


@app.put('/book')
def update_book():
    data = request.get_json()
    id = str(data['id'])
    title = data['title']
    price = str(data['price'])
    description = data['description']
    author_id = data['author_id']

    with connection:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE book SET title = '" + title + "', price = '" + price + "', description = '" + description + "', author_id = '" + author_id + "' WHERE id = '" + id + "';")
    return 'Data added'


@app.delete('/book/<int:book_id>')
def delete_book(book_id):
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM book where id = '" + str(book_id) + "';")
    return 'Book deleted'


@app.get('/books')
@token_required
def add_book():
    with connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM book;")
            data = cursor.fetchall()
    return jsonify(data)


@app.route('/login')
def login():
    auth = request.authorization

    if auth and auth.password == 'password':
        token = jwt.encode({'user': auth.username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=30)}, secret_key, algorithms=["HS256"])
        return jsonify({'token': token})

    return make_response('Could not verify!', 401, {'WWW-Authenticate': 'Basic realm="Login Required"'})


if __name__ == '__main__':
    app.run()
