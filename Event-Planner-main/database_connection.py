from flask import Flask, request, render_template, redirect, url_for, session, flash
from datetime import datetime
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
    is_admin = session.get('role') == "admin"
    user_id = session.get('username')  # get current user

    # connect to the DB and get which events this user registered for
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "events.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT event_id FROM registrations WHERE user_id = ?", (user_id,))
    registered_event_ids = {row[0] for row in cursor.fetchall()}
    conn.close()

    # ✅ Now pass `registered_event_ids` to the template
    return render_template('view_events.html', events=events, is_admin=is_admin, registered_event_ids=registered_event_ids)

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
        military_time = request.form.get('time')
        dt = datetime.strptime(military_time, "%H:%M")
        time = dt.strftime("%I:%M%p")
        if time.startswith("0"):
            time = time[1:]
        location = request.form.get('location')
        event_creator = session.get('username')  # Get event creator from session
        max_attendees = request.form.get('max_attendees')

        if not event_creator:
            flash("Error: No event creator found.")
            return redirect(url_for('add_event'))

        # Add event to the database

        # Dynamically determine the database path based on the script's location
        BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
        db_path = os.path.join(BASE_DIR, "events.db") 
        conn = sqlite3.connect(db_path)

        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (event_title, event_date, event_time, event_location, max_attendees, event_creator) VALUES (?, ?, ?, ?, ?, ?)", 
               (title, date, time, location, max_attendees, event_creator))

        conn.commit()
        conn.close()

        flash("Event added successfully.")
        return redirect(url_for('view_events'))

    return render_template('create_eventpage.html')
# Edit Events     
@app.route('/edit_event/<event_title>', methods=['GET', 'POST'])
def edit_event(event_title):
    if 'username' not in session or session.get('role') != 'admin':
        flash("You must be an admin to edit events.")
        return redirect(url_for('view_events'))

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
        new_attendees = request.form.get('max_attendees')

        # Update the event in the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE events 
            SET event_title = ?, event_date = ?, event_time = ?, event_location = ?, max_attendees = ?
            WHERE event_title = ?
        """, (new_title, new_date, new_time, new_location, new_attendees, event_title))
        conn.commit()
        conn.close()

        flash("Event updated successfully.")
        return redirect(url_for('view_events'))

    return render_template('edit_eventpage.html', event=event)

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


# Register for event
@app.route('/register_event', methods=['POST'])
def register_event():
    if 'username' not in session:
        flash("Please log in to register for events.")
        return redirect(url_for('login_page'))  

    event_id = request.form.get('event_id')
    event_title = request.form.get('event_title')
    user_id = session.get('username')

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(BASE_DIR, "events.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM registrations WHERE user_id = ? AND event_id = ?", (user_id, event_id))
    if cursor.fetchone():
        flash("You are already registered for this event.")
    else:
        cursor.execute("INSERT INTO registrations (user_id, event_id, event_title) VALUES (?, ?, ?)",
                       (user_id, event_id, event_title))
        conn.commit()
        flash(f"Successfully registered for {event_title}!")

    conn.close()
    return redirect(url_for('view_events'))

# Admin-only route to logout
@app.route('/logout')
def logout():
    session.clear()  
    flash("You have been logged out.")
    return redirect(url_for('login_page'))

#route to display events that current user or organizer are registered to
@app.route('/my_registrations')
def my_registrations():
    if 'username' not in session:
        flash("Please log in to view your registrations.")
        return redirect(url_for('login_page'))

    user_id = session['username']

    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
    db_path = os.path.join(BASE_DIR, "events.db") 
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        SELECT e.event_title, e.event_date, e.event_time, e.event_location
        FROM events e
        JOIN registrations r ON e.event_title = r.event_title
        WHERE r.user_id = ?
        ORDER BY e.event_date ASC
    """, (user_id,))

    registered_events = cursor.fetchall()
    conn.close()

    return render_template('my_registrations.html', registered_events=registered_events)


# Run the application
if __name__ == "__main__":
    app.run(debug=True)