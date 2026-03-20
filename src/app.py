"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Database setup
# ---------------------------------------------------------------------------

current_dir = Path(__file__).parent
DATABASE_URL = f"sqlite:///{current_dir}/activities.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


class Activity(SQLModel, table=True):
    name: str = Field(primary_key=True)
    description: str
    schedule: str
    max_participants: int


class Participant(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    activity_name: str = Field(foreign_key="activity.name", index=True)
    email: str


# ---------------------------------------------------------------------------
# Seed data
# ---------------------------------------------------------------------------

_SEED_ACTIVITIES = [
    Activity(name="Chess Club", description="Learn strategies and compete in chess tournaments",
             schedule="Fridays, 3:30 PM - 5:00 PM", max_participants=12),
    Activity(name="Programming Class", description="Learn programming fundamentals and build software projects",
             schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM", max_participants=20),
    Activity(name="Gym Class", description="Physical education and sports activities",
             schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", max_participants=30),
    Activity(name="Soccer Team", description="Join the school soccer team and compete in matches",
             schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM", max_participants=22),
    Activity(name="Basketball Team", description="Practice and play basketball with the school team",
             schedule="Wednesdays and Fridays, 3:30 PM - 5:00 PM", max_participants=15),
    Activity(name="Art Club", description="Explore your creativity through painting and drawing",
             schedule="Thursdays, 3:30 PM - 5:00 PM", max_participants=15),
    Activity(name="Drama Club", description="Act, direct, and produce plays and performances",
             schedule="Mondays and Wednesdays, 4:00 PM - 5:30 PM", max_participants=20),
    Activity(name="Math Club", description="Solve challenging problems and participate in math competitions",
             schedule="Tuesdays, 3:30 PM - 4:30 PM", max_participants=10),
    Activity(name="Debate Team", description="Develop public speaking and argumentation skills",
             schedule="Fridays, 4:00 PM - 5:30 PM", max_participants=12),
]

_SEED_PARTICIPANTS = [
    ("Chess Club", "michael@mergington.edu"),
    ("Chess Club", "daniel@mergington.edu"),
    ("Programming Class", "emma@mergington.edu"),
    ("Programming Class", "sophia@mergington.edu"),
    ("Gym Class", "john@mergington.edu"),
    ("Gym Class", "olivia@mergington.edu"),
    ("Soccer Team", "liam@mergington.edu"),
    ("Soccer Team", "noah@mergington.edu"),
    ("Basketball Team", "ava@mergington.edu"),
    ("Basketball Team", "mia@mergington.edu"),
    ("Art Club", "amelia@mergington.edu"),
    ("Art Club", "harper@mergington.edu"),
    ("Drama Club", "ella@mergington.edu"),
    ("Drama Club", "scarlett@mergington.edu"),
    ("Math Club", "james@mergington.edu"),
    ("Math Club", "benjamin@mergington.edu"),
    ("Debate Team", "charlotte@mergington.edu"),
    ("Debate Team", "henry@mergington.edu"),
]


def _seed_database():
    """Populate the database with starter data if it is empty."""
    with Session(engine) as session:
        if session.exec(select(Activity)).first():
            return  # Already seeded
        for activity in _SEED_ACTIVITIES:
            session.add(activity)
        session.commit()
        for activity_name, email in _SEED_PARTICIPANTS:
            session.add(Participant(activity_name=activity_name, email=email))
        session.commit()


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    SQLModel.metadata.create_all(engine)
    _seed_database()
    yield


app = FastAPI(
    title="Mergington High School API",
    description="API for viewing and signing up for extracurricular activities",
    lifespan=lifespan,
)

app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    with Session(engine) as session:
        db_activities = session.exec(select(Activity)).all()
        result = {}
        for activity in db_activities:
            participants = session.exec(
                select(Participant).where(Participant.activity_name == activity.name)
            ).all()
            result[activity.name] = {
                "description": activity.description,
                "schedule": activity.schedule,
                "max_participants": activity.max_participants,
                "participants": [p.email for p in participants],
            }
        return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    with Session(engine) as session:
        activity = session.get(Activity, activity_name)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        already_signed_up = session.exec(
            select(Participant).where(
                Participant.activity_name == activity_name,
                Participant.email == email,
            )
        ).first()
        if already_signed_up:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        participant_count = len(
            session.exec(
                select(Participant).where(Participant.activity_name == activity_name)
            ).all()
        )
        if participant_count >= activity.max_participants:
            raise HTTPException(status_code=400, detail="Activity is full")

        session.add(Participant(activity_name=activity_name, email=email))
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    with Session(engine) as session:
        activity = session.get(Activity, activity_name)
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        participant = session.exec(
            select(Participant).where(
                Participant.activity_name == activity_name,
                Participant.email == email,
            )
        ).first()
        if not participant:
            raise HTTPException(
                status_code=400,
                detail="Student is not signed up for this activity",
            )

        session.delete(participant)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
