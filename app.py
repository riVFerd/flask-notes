import os
from os.path import dirname, join
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request, session, redirect
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

client = MongoClient(os.environ.get('MONGODB_URI'))
db = client[os.environ.get('DB_NAME')]

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')


# function helpers
def get_user_id(username):
    # Find the user with the matching username
    user = db.users.find_one({'username': username})
    if user:
        # Return the user's ID if the user was found
        return user['_id']
    else:
        # Return None if the user was not found
        return None


def get_user(user_id):
    # Find the user with the matching ID
    user = db.users.find_one({'_id': user_id})
    if user:
        # Return the user's data if the user was found
        return user
    else:
        # Return None if the user was not found
        return None


# end function helpers

# request handlers
@app.route('/login', methods=['POST'])
def login():
    # Validate the user's credentials
    user = db.users.find_one({'username': request.form['username']})
    if user is None:
        return jsonify({'message': 'username does not exist', 'error': True})
    elif user['password'] != request.form['password']:
        return jsonify({'message': 'incorrect password', 'error': True})
    return jsonify({'message': 'success', 'error': False})


# end request handlers

@app.route('/')
def home_page():
    if session.get('username'):
        # If the user is logged in, display the home page
        return render_template('index.html')
    return render_template('login.html')


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)
