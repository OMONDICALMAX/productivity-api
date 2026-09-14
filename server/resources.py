from flask import request
from flask_jwt_extended import jwt_required, get_jwt_identity

from server.app import app, db
from server.models import Note


@app.route("/notes", methods=["POST"])
@jwt_required()
def create_note():
    user_id = get_jwt_identity()

    data = request.get_json()

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return {
            "error": "title and content are required"
        }, 400

    note = Note(
        title=title,
        content=content,
        user_id=int(user_id)
    )

    db.session.add(note)
    db.session.commit()

    return {
        "message": "Note created successfully",
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "user_id": note.user_id,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }, 201

@app.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()

    notes = Note.query.filter_by(user_id=int(user_id)).all()

    return {
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "user_id": note.user_id,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            for note in notes
        ]
    }, 200

@app.route("/notes", methods=["GET"])
@jwt_required()
def get_notes():
    user_id = get_jwt_identity()

    page = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 5, type=int)

    if page < 1:
        page = 1

    if per_page < 1:
        per_page = 5

    pagination = Note.query.filter_by(
        user_id=int(user_id)
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )

    return {
        "notes": [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "user_id": note.user_id,
                "created_at": note.created_at.isoformat(),
                "updated_at": note.updated_at.isoformat()
            }
            for note in pagination.items
        ],
        "pagination": {
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
            "has_next": pagination.has_next,
            "has_prev": pagination.has_prev
        }
    }, 200

@app.route("/notes/<int:note_id>", methods=["PATCH"])
@jwt_required()
def update_note(note_id):
    user_id = get_jwt_identity()

    note = Note.query.filter_by(
        id=note_id,
        user_id=int(user_id)
    ).first()

    if not note:
        return {
            "error": "Note not found"
        }, 404

    data = request.get_json()

    if "title" in data:
        note.title = data["title"]

    if "content" in data:
        note.content = data["content"]

    if not note.title or not note.content:
        return {
            "error": "title and content cannot be empty"
        }, 400

    db.session.commit()

    return {
        "message": "Note updated successfully",
        "note": {
            "id": note.id,
            "title": note.title,
            "content": note.content,
            "user_id": note.user_id,
            "created_at": note.created_at.isoformat(),
            "updated_at": note.updated_at.isoformat()
        }
    }, 200

@app.route("/notes/<int:note_id>", methods=["DELETE"])
@jwt_required()
def delete_note(note_id):
    user_id = get_jwt_identity()

    note = Note.query.filter_by(
        id=note_id,
        user_id=int(user_id)
    ).first()

    if not note:
        return {
            "error": "Note not found"
        }, 404

    db.session.delete(note)
    db.session.commit()

    return "", 204