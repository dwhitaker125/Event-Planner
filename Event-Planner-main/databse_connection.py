from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = "your_secret_key"  # Required for session handling

# Route for the login page
@app.route('/')
def login_page():
    return render_template('login.html')

# Route to handle login
@app.route('/login', methods=['POST'])
def login():

    username = request.form.get('username')
    password = request.form.get('password')

    conn = sqlite3.connect("students.db")
    cursor = conn.cursor()

    # Check user credentials
    cursor.execute("SELECT * FROM students WHERE id = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        session['username'] = username  # Store session data
        return redirect(url_for('view_events'))  # Redirect to events page
    else:
        flash("Invalid username or password. Please try again.")  # Flash message for pop-up
        return redirect(url_for('login_page'))  # Stay on login page

# Route to get information for the events page
def get_events():
    conn = sqlite3.connect("events.db") 
    cursor = conn.cursor()
    cursor.execute("SELECT event_title, event_date, event_time, event_location FROM events") 
    events = cursor.fetchall()
    conn.close()
    return events

# Route for displaying events
@app.route('/events')
def view_events():
    events = get_events()  
    return render_template('view_events.html', events=events)

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
