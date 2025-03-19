from flask import Flask, request, render_template, redirect, url_for, session, flash
import os
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
            return redirect(url_for('view_events'))  # Redirect admin to event management
        else:
            return redirect(url_for('view_events'))  # Redirect regular user to events page
    else:
        flash("Invalid username or password. Please try again.")  
        return redirect(url_for('login_page'))  

# Function to fetch events from the database
def get_events():
    conn = sqlite3.connect("events.db") 
    cursor = conn.cursor()
    cursor.execute("SELECT event_title, event_date, event_time, event_location FROM events ORDER BY event_date ASC")
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
    is_admin = session.get('role') == "admin"  # Check if the user is an admin

    return render_template('view_events.html', events=events, is_admin=is_admin)

# Admin-only route to add a new event
@app.route('/add_event', methods=['GET', 'POST'])
def add_event():
    if 'username' not in session or session.get('role') != 'admin':
        flash("You must be an admin to access this page.")
        return redirect(url_for('view_events'))

    if request.method == 'POST':
        # Get event details from the form
        title = request.form.get('title')
        date = request.form.get('date')
        time = request.form.get('time')
        location = request.form.get('location')
        event_creator = session.get('username')  # Get event creator from session

        if not event_creator:
            flash("Error: No event creator found.")
            return redirect(url_for('add_event'))

        # Add event to the database

        # Dynamically determine the database path based on the script's location
        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
        db_path = os.path.join(BASE_DIR, "events.db") 
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (event_title, event_date, event_time, event_location, event_creator) VALUES (?, ?, ?, ?, ?)", 
                       (title, date, time, location, event_creator))
        conn.commit()
        conn.close()

        flash("Event added successfully.")
        return redirect(url_for('view_events'))

    return render_template('create_eventpage.html')

# Admin-only route to delete an event
@app.route('/delete_event', methods=['GET', 'POST'])
def delete_event():
    if 'username' not in session or session.get('role') != 'admin':
        flash("You must be an admin to access this page.")
        return redirect(url_for('view_events'))

    if request.method == 'POST':
        # Get event details from the form
        event_info = request.form.get('event_info')

        if not event_info:
            flash("Error: No event selected.")
            return redirect(url_for('delete_event'))

        # Split the event_info to extract title, date, and time
        event_title, event_date, event_time = event_info.split('|')

        # Dynamically determine the database path based on the script's location
        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
        db_path = os.path.join(BASE_DIR, "events.db")
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()
        cursor.execute("DELETE FROM events WHERE event_title = ? AND event_date = ? AND event_time = ?", (event_title.strip(), event_date.strip(), event_time.strip()))
        conn.commit()
        conn.close()

        flash("Event deleted successfully.")
        return redirect(url_for('view_events'))

    # Display all events for deletion
    events = get_events()
    return render_template('delete_eventpage.html', events=events)



# Admin-only route to logout
@app.route('/logout')
def logout():
    session.clear()  
    flash("You have been logged out.")
    return redirect(url_for('login_page'))

# Run the application
if __name__ == "__main__":
    app.run(debug=True)
