from flask import Flask, request, render_template, redirect, url_for

import sqlite3

app = Flask(__name__)

# Route for the login page
@app.route('/')
def login_page():
    return render_template('login.html')  # Ensure this matches your HTML filename

# Route to handle the login form submission
@app.route('/login', methods=['POST'])
def login():
    # Get form data
    username = request.form.get('username')
    password = request.form.get('password')

    # Connect to the database
    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Check if the username and password match
    cursor.execute("SELECT * FROM students WHERE id = ? AND password = ?", (username, password))
    user = cursor.fetchone()

    conn.close()

    # Verify user credentials
    if user:
        return f"Welcome, {username}!"
    else:
        return "Invalid username or password. Please try again."

# Run the application
if __name__ == "__main__":
    app.run(debug=True)

