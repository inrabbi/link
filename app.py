from flask import Flask, request, redirect, render_template, url_for
import sqlite3
import os
from utils.helpers import generate_short_code
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def init_db():
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    db_dir = os.path.dirname(db_path)
    
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir)

    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS urls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                long_url TEXT NOT NULL,
                short_code TEXT NOT NULL UNIQUE
            )
        ''')
        conn.commit()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        long_url = request.form['long_url']
        custom_code = request.form.get('custom_code')  # Optional custom code

        if not custom_code:
            custom_code = generate_short_code()  # Generate a random short code if not provided

        db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            # Check if the custom code already exists
            cursor.execute('SELECT id FROM urls WHERE short_code = ?', (custom_code,))
            existing_code = cursor.fetchone()
            if existing_code:
                return render_template('index.html', error="Custom code already exists. Please try a different one.")

            # Insert into the database
            cursor.execute('INSERT INTO urls (long_url, short_code) VALUES (?, ?)', (long_url, custom_code))
            conn.commit()

        short_url = url_for('redirect_to_long_url', short_code=custom_code, _external=True)
        return render_template('index.html', short_url=short_url)

    return render_template('index.html')

@app.route('/<short_code>')
def redirect_to_long_url(short_code):
    db_path = app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', '')
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT long_url FROM urls WHERE short_code = ?', (short_code,))
        result = cursor.fetchone()

        if result:
            return redirect(result[0])
        else:
            return "URL not found", 404

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
