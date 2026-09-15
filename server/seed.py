from server.app import app, db, bcrypt
from server.models import User, Note


with app.app_context():
    user = User.query.filter_by(username="seeduser").first()

    if not user:
        user = User(
            username="seeduser",
            email="seed@example.com",
            password_hash=bcrypt.generate_password_hash(
                "secret123"
            ).decode("utf-8")
        )

        db.session.add(user)
        db.session.commit()

    if not user.notes:
        notes = [
            Note(
                title="Note 1",
                content="This is the first seeded note.",
                user_id=user.id
            ),
            Note(
                title="Note 2",
                content="This is the second seeded note.",
                user_id=user.id
            ),
            Note(
                title="Note 3",
                content="This is the third seeded note.",
                user_id=user.id
            ),
            Note(
                title="Note 4",
                content="This is the fourth seeded note.",
                user_id=user.id
            ),
            Note(
                title="Note 5",
                content="This is the fifth seeded note.",
                user_id=user.id
            ),
            Note(
                title="Note 6",
                content="This is the sixth seeded note.",
                user_id=user.id
            ),
            Note(
                title="Note 7",
                content="This is the seventh seeded note.",
                user_id=user.id
            )
        ]

        db.session.add_all(notes)
        db.session.commit()

    print("Database seeded successfully.")