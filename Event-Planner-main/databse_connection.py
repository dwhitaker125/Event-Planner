from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3, os

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

    # Dynamically determine the database path based on the script's location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
    db_path = os.path.join(BASE_DIR, "students.db") 

    conn = sqlite3.connect(db_path)
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

    # Dynamically determine the database path based on the script's location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
    db_path = os.path.join(BASE_DIR, "events.db") 

    conn = sqlite3.connect(db_path) 
    cursor = conn.cursor()
    cursor.execute("SELECT event_title, event_date, event_time, event_location, max_attendees FROM events ORDER BY event_date ASC")
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

#Edit events for admin
@app.route('/edit_event/<event_title>', methods=['GET', 'POST'])
def edit_event(event_title):
    if 'username' not in session or session.get('role') != 'admin':
        flash("You must be an admin to edit events.")
        return redirect(url_for('view_events'))

    # Determine database path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "events.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch event details
    cursor.execute("SELECT event_title, event_date, event_time, event_location FROM events WHERE event_title = ?", (event_title,))
    event = cursor.fetchone()
    conn.close()

    if not event:
        flash("Event not found.")
        return redirect(url_for('view_events'))

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_date = request.form.get('date')
        new_time = request.form.get('time')
        new_location = request.form.get('location')

        # Update the event in the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE events 
            SET event_title = ?, event_date = ?, event_time = ?, event_location = ?
            WHERE event_title = ?
        """, (new_title, new_date, new_time, new_location, event_title))
        conn.commit()
        conn.close()

        flash("Event updated successfully.")
        return redirect(url_for('view_events'))

    return render_template('edit_event.html', event=event)


# Admin-only route to delete events
@app.route('/delete_event/<event_title>', methods=['POST'])
def delete_event(event_title):
    if 'username' not in session or session.get('role') != 'admin':
        flash("You must be an admin to delete events.")
        return redirect(url_for('view_events'))

    # Dynamically determine the database path based on the script's location
    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
    db_path = os.path.join(BASE_DIR, "events.db") 
    conn = sqlite3.connect(db_path)

    cursor = conn.cursor()
    cursor.execute("DELETE FROM events WHERE event_title = ?", (event_title,))
    conn.commit()
    conn.close()

    flash("Event deleted successfully.")
    return redirect(url_for('view_events'))

# Admin-only route to logout
@app.route('/logout')
def logout():
    session.clear()  
    flash("You have been logged out.")
    return redirect(url_for('login_page'))

# Run the application
if __name__ == "__main__":
    app.run(debug=True)