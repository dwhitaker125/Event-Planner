from flask import Flask, request, render_template, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session management

@app.route('/')
def login_page():
    return render_template('login_v1.1.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM students WHERE id = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    
    conn.close()

    if user:
        session['user_id'] = username  # Store user session
        return redirect(url_for('view_events'))
    else:
        return render_template('login_v1.1.html')

@app.route('/view_events')
def view_events():
    if 'user_id' in session:
        return render_template('view_events_v1.1.html')  # Ensure this file exists
    else:
        return redirect(url_for('login_page'))  # Redirect to login if not authenticated

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user session
    return redirect(url_for('login_page'))

if __name__ == "__main__":
    app.run(debug=True)
