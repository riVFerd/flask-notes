import os
from os.path import dirname, join
from dotenv import load_dotenv
from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

client = MongoClient(os.environ.get('MONGODB_URI'))
db = client['DB_NAME']

app = Flask(__name__)

@app.route('/')
def home_page():
    return render_template('index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)