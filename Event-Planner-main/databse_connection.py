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

    # Fetch user ID and role
    cursor.execute("SELECT id, role FROM students WHERE id = ? AND password = ?", (username, password))
    user = cursor.fetchone()
    conn.close()

    if user:
        user_id, role = user  
        session['username'] = username  
        session['role'] = role  

        if role == "admin":
            return redirect(url_for('admin_events'))  # Redirect admin to event management
        else:
            return redirect(url_for('view_events'))  # Redirect regular user to events page
    else:
        flash("Invalid username or password. Please try again.")  
        return redirect(url_for('login_page'))  

# Function to fetch events from the database
def get_events():
    conn = sqlite3.connect("events.db") 
    cursor = conn.cursor()
    cursor.execute("SELECT event_title, event_date, event_time, event_location FROM events") 
    events = cursor.fetchall()
    conn.close()
    return events

# Route for displaying events (Regular User)
@app.route('/events')
def view_events():
    if 'username' not in session:
        flash("Please log in to view events.")
        return redirect(url_for('login_page'))  

    events = get_events()  

    return render_template('view_events.html', events=events)

# Route for Admin Event Management
@app.route('/admin/events')
def admin_events():
    if 'username' not in session or session.get('role') != "admin":
        flash("Unauthorized access.")
        return redirect(url_for('view_events'))  

    events = get_events()  

    return render_template('admin_v1.1.html', events=events)

# Logout Route
@app.route('/logout')
def logout():
    session.clear()  
    flash("You have been logged out.")
    return redirect(url_for('login_page'))

# Run the application
if __name__ == "__main__":
    app.run(debug=True)

