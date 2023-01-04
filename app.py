import os
from os.path import dirname, join
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, session, redirect
from pymongo import MongoClient

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

# find user by username then return user_id
def get_user_id(username):
    user = db.users.find_one({'username': username})
    if user:
        return user['_id']
    else:
        return None


# find user by username then return object user
def get_user_by_name(username):
    user = db.users.find_one({'username': username})
    if user:
        return user
    else:
        return None


# find user by user_id then return object user
def get_user(user_id):
    user = db.users.find_one({'_id': user_id})
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
    session['user_id'] = user['_id']
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


# end request handlers

@app.route('/')
def home_page():
    if session.get('username'):
        # If the user is logged in, display the home page
        return render_template('index.html')
    return redirect('/login')


@app.route('/login')
def login_page():
    return render_template('login.html')


@app.route('/signup')
def signup_page():
    return render_template('signup.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
