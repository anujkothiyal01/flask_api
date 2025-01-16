from flask import Flask, render_template, request, redirect, session, url_for, jsonify
from pymongo import MongoClient
from flask_cors import CORS  # Import CORS
import os

app = Flask(__name__)
app.secret_key = "your_secret_key"

# Enable CORS for all routes
CORS(app)

# MongoDB setup
MONGO_URI = "mongodb+srv://kothiyalofficial:cQeqY8hnef8B8AK3@cluster0.tzgns.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(MONGO_URI)
db = client['usercards']
users = db['users']
cards = db['cards']

# Home Route
@app.route('/')
def home():
    return render_template("index.html")

# Registration Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check if the username is already taken
        if users.find_one({'username': username}):
            return "Username already exists. Try another one."

        # Add new user
        users.insert_one({'username': username, 'password': password})
        return redirect('/login')
    return render_template('register.html')

# Login Route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = users.find_one({'username': username, 'password': password})
        if user:
            session['username'] = username
            return redirect('/dashboard')
        return "Invalid credentials. Try again."
    return render_template('login.html')

# Dashboard Route
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'username' not in session:
        return redirect('/login')

    if request.method == 'POST':
        name = request.form['name']
        skills = request.form['skills']
        phone = request.form['phone']
        linkedin = request.form['linkedin']

        # Create or update card for the user
        cards.update_one(
            {'username': session['username']},
            {'$set': {'name': name, 'skills': skills, 'phone': phone, 'linkedin': linkedin}},
            upsert=True
        )
        return redirect(url_for('user_card', username=session['username']))

    return render_template('dashboard.html', username=session['username'])

# Dynamic Route for User Card
@app.route('/<username>')
def user_card(username):
    card = cards.find_one({'username': username})
    if not card:
        return "Card not found.", 404

    return render_template('card.html', card=card)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
