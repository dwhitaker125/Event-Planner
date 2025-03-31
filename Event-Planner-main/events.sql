ALTER TABLE events ADD COLUMN max_attendees INTEGER;

UPDATE events SET max_attendees = attendees;
CREATE TABLE events_new AS SELECT event_title, event_date, event_time, event_location, event_creator, max_attendees FROM events;
DROP TABLE events;
ALTER TABLE events_new RENAME TO events;
