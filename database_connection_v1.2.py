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
    user_id = session.get('username')

    # Get registered event IDs for the user
    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()
    cursor.execute("SELECT event_id FROM registrations WHERE user_id = ?", (user_id,))
    registered_event_ids = {row[0] for row in cursor.fetchall()}  # Store event IDs in a set
    conn.close()

    return render_template('view_events.html', events=events, registered_event_ids=registered_event_ids)

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
        conn = sqlite3.connect("events.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO events (event_title, event_date, event_time, event_location, event_creator) VALUES (?, ?, ?, ?, ?)", 
                       (title, date, time, location, event_creator))
        conn.commit()
        conn.close()

        flash("Event added successfully.")
        return redirect(url_for('view_events'))

    return render_template('create_eventpage.html')

# Admin-only route to edit an event
@app.route('/logout')
def logout():
    session.clear()  
    flash("You have been logged out.")
    return redirect(url_for('login_page'))

@app.route('/register_event', methods=['POST'])
def register_event():
    if 'username' not in session:
        flash("Please log in to register for events.")
        return redirect(url_for('login_page'))  

    event_id = request.form.get('event_id')  # Get event_id from form
    event_title = request.form.get('event_title')  # Get event_title
    user_id = session.get('username')  # Use username as user ID

    conn = sqlite3.connect("events.db")
    cursor = conn.cursor()

    # Check if user is already registered for this event
    cursor.execute("SELECT * FROM registrations WHERE user_id = ? AND event_id = ?", (user_id, event_id))
    existing_registration = cursor.fetchone()

    if existing_registration:
        flash("You are already registered for this event.", "warning")
    else:
        # Insert into registrations table
        cursor.execute("INSERT INTO registrations (user_id, event_id, event_title) VALUES (?, ?, ?)", 
                       (user_id, event_id, event_title))
        conn.commit()
        flash(f"Successfully registered for {event_title}!", "success")

    conn.close()
    return redirect(url_for('view_events'))


# Run the application
if __name__ == "__main__":
    app.run(debug=True)
