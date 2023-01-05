import os
from os.path import dirname, join
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, session, redirect
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId

# load environment variables
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

# set up connection to MongoDB
client = MongoClient(os.environ.get('MONGODB_URI'))
db = client[os.environ.get('DB_NAME')]

# set up Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


# function helpers


# find user by username then return object user
def get_user_by_name(username):
    user = db.users.find_one({'username': username})
    if user:
        return user
    else:
        return None


# end function helpers

# request handlers
@app.route('/login', methods=['POST'])
def login():
    # Validate the user's credentials
    user = get_user_by_name(request.form['username'])
    if user is None:
        return jsonify({'message': 'username does not exist!', 'status': False})
    elif user['password'] != request.form['password']:
        return jsonify({'message': 'incorrect password!', 'status': False})
    session['user_id'] = str(user['_id'])
    session['username'] = user['username']
    return jsonify({'message': 'login success!', 'status': True})


@app.route('/signup', methods=['POST'])
def signup():
    # Validate the user's credentials
    user = get_user_by_name(request.form['username'])
    if user is not None:
        return jsonify({'message': 'username already exists!', 'status': False})

    # Create a new user
    username = request.form['username']
    email = request.form['email']
    user_id = db.users.insert_one({
        'username': username,
        'email': email,
        'password': request.form['password']
    }).inserted_id

    # set session
    session['user_id'] = str(user_id)
    session['username'] = username
    return jsonify({'message': 'signup success!', 'status': True})


@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('user_id', None)
    session.pop('username', None)
    return redirect('/')


@app.route('/create_note', methods=['POST'])
def create_note():
    if 'user_id' not in session:
        return jsonify({'message': 'login required!', 'status': False})

    result = db.notes.insert_one({
        'title': request.form['title'],
        'content': request.form['content'],
        'updated_at': datetime.now(),
        'user_id': session['user_id']
    })

    if result.inserted_id:
        return jsonify({'message': 'create note success!', 'status': True})


@app.route('/note_detail', methods=['POST'])
def note_detail():
    if 'user_id' not in session:
        return jsonify({'message': 'login required!', 'status': False})

    note = db.notes.find_one({'_id': ObjectId(request.form['note_id'])})
    if note:
        note['_id'] = str(note['_id'])
        return jsonify({'message': 'get note success!', 'status': True, 'note': note})
    return jsonify({'message': 'note not found!', 'status': False})


@app.route('/delete_note', methods=['POST'])
def delete_note():
    if 'user_id' not in session:
        return jsonify({'message': 'login required!', 'status': False})

    result = db.notes.delete_one({'_id': ObjectId(request.form['note_id'])})
    if result.deleted_count:
        return jsonify({'message': 'delete note success!', 'status': True})
    return jsonify({'message': 'note not found!', 'status': False})


@app.route('/update_note', methods=['POST'])
def update_note():
    if 'user_id' not in session:
        return jsonify({'message': 'login required!', 'status': False})

    result = db.notes.update_one({'_id': ObjectId(request.form['note_id'])}, {
        '$set': {
            'title': request.form['title'],
            'content': request.form['content'],
            'updated_at': datetime.now()
        }
    })
    if result.modified_count:
        return jsonify({'message': 'update note success!', 'status': True})
    return jsonify({'message': 'note not found!', 'status': False})


# end request handlers

@app.route('/')
def home_page():
    if session.get('username'):
        # get all notes of user
        notes = db.notes.find({'user_id': session['user_id']})
        # If the user is logged in, display the home page
        return render_template('index.html', notes=notes)
    return redirect('/login')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
