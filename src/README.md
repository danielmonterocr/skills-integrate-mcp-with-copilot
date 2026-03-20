# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Data is persisted in a local SQLite database and survives server restarts

## Getting Started

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

   Or install directly:

   ```
   pip install fastapi uvicorn sqlmodel
   ```

2. Run the application:

   ```
   uvicorn app:app --reload
   ```

   On first startup the app will automatically:
   - Create the SQLite database file (`activities.db`) in the `src/` directory.
   - Run table migrations (`CREATE TABLE IF NOT EXISTS`).
   - Seed the database with the default activities and participants (only if the database is empty).

   To force a fresh seed, delete `src/activities.db` and restart the server.

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister a student from an activity                           |

## Data Model

The application uses SQLite (via SQLModel / SQLAlchemy) with two tables:

1. **Activity** — identified by name:
   - `name` (primary key)
   - `description`
   - `schedule`
   - `max_participants`

2. **Participant** — represents a signup:
   - `id` (auto-increment primary key)
   - `activity_name` (foreign key → Activity.name)
   - `email`
