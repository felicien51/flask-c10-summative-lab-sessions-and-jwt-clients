from flask import request, session
from flask_restful import Resource
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError

from config import db
from models import User
from schemas import SignUpSchema, LoginSchema

signup_schema = SignUpSchema()
login_schema = LoginSchema()


class SignUp(Resource):
    def post(self):
        try:
            data = signup_schema.load(request.get_json() or {})
        except ValidationError as err:
            return {"errors": _flatten_errors(err.messages)}, 422

        if data["password"] != data["password_confirmation"]:
            return {"errors": ["Password and password confirmation must match"]}, 422

        user = User(username=data["username"])
        try:
            user.password_hash = data["password"]
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username already taken"]}, 422
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 422

        session["user_id"] = user.id
        return user.to_dict(), 201


class Login(Resource):
    def post(self):
        try:
            data = login_schema.load(request.get_json() or {})
        except ValidationError as err:
            return {"errors": _flatten_errors(err.messages)}, 422

        user = User.query.filter_by(username=data["username"]).first()

        if user and user.authenticate(data["password"]):
            session["user_id"] = user.id
            return user.to_dict(), 200

        return {"errors": ["Invalid username or password"]}, 401


class Logout(Resource):
    def delete(self):
        if session.get("user_id"):
            session["user_id"] = None
            return {}, 204
        return {"errors": ["Not logged in"]}, 401


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if user_id:
            user = User.query.get(user_id)
            if user:
                return user.to_dict(), 200
        return {"errors": ["Not authorized"]}, 401


def _flatten_errors(messages):
    errors = []
    for field, msgs in messages.items():
        for msg in msgs:
            errors.append(f"{field}: {msg}")
    return errors
