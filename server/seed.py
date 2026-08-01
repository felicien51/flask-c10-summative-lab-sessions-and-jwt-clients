import random
from datetime import timedelta

from faker import Faker

from app import app
from config import db
from models import User, Task

fake = Faker()

PRIORITIES = ["low", "medium", "high"]


def seed():
    with app.app_context():
        print("Clearing existing data...")
        Task.query.delete()
        User.query.delete()
        db.session.commit()

        print("Seeding users...")
        users = []
        # A predictable demo user for easy manual testing / grading.
        demo = User(username="demo")
        demo.password_hash = "password123"
        db.session.add(demo)
        users.append(demo)

        for _ in range(4):
            user = User(username=fake.unique.user_name())
            user.password_hash = "password123"
            db.session.add(user)
            users.append(user)

        db.session.commit()

        print("Seeding tasks...")
        for user in users:
            for _ in range(random.randint(6, 12)):
                task = Task(
                    title=fake.sentence(nb_words=4).rstrip("."),
                    description=fake.paragraph(nb_sentences=2),
                    priority=random.choice(PRIORITIES),
                    completed=random.choice([True, False]),
                    due_date=fake.date_between(
                        start_date="today", end_date=timedelta(days=30)
                    ),
                    user_id=user.id,
                )
                db.session.add(task)

        db.session.commit()
        print(f"Done! Seeded {len(users)} users and their tasks.")
        print("Demo login -> username: 'demo', password: 'password123'")


if __name__ == "__main__":
    seed()
