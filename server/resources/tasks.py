from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db
from models import Task
from schemas import TaskSchema, TaskUpdateSchema
from decorators import login_required

task_schema = TaskSchema()
task_update_schema = TaskUpdateSchema()


def _flatten_errors(messages):
    errors = []
    for field, msgs in messages.items():
        for msg in msgs:
            errors.append(f"{field}: {msg}")
    return errors


class TaskList(Resource):
    @login_required
    def get(self, current_user):
        try:
            page = int(request.args.get("page", 1))
            per_page = int(request.args.get("per_page", 10))
        except ValueError:
            return {"errors": ["page and per_page must be integers"]}, 422

        page = max(page, 1)
        per_page = min(max(per_page, 1), 100)

        query = Task.query.filter_by(user_id=current_user.id).order_by(
            Task.created_at.desc()
        )
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        return {
            "tasks": [task.to_dict() for task in pagination.items],
            "meta": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "total_pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            },
        }, 200

    @login_required
    def post(self, current_user):
        try:
            data = task_schema.load(request.get_json() or {})
        except ValidationError as err:
            return {"errors": _flatten_errors(err.messages)}, 422

        task = Task(user_id=current_user.id, **data)
        try:
            db.session.add(task)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 422

        return task.to_dict(), 201


class TaskDetail(Resource):
    def _get_owned_task(self, id, current_user):
        task = Task.query.get(id)
        if not task or task.user_id != current_user.id:
            return None
        return task

    @login_required
    def get(self, id, current_user):
        task = self._get_owned_task(id, current_user)
        if not task:
            return {"errors": ["Task not found"]}, 404
        return task.to_dict(), 200

    @login_required
    def patch(self, id, current_user):
        task = self._get_owned_task(id, current_user)
        if not task:
            return {"errors": ["Task not found"]}, 404

        try:
            data = task_update_schema.load(request.get_json() or {}, partial=True)
        except ValidationError as err:
            return {"errors": _flatten_errors(err.messages)}, 422

        try:
            for attr, value in data.items():
                setattr(task, attr, value)
            db.session.commit()
        except ValueError as err:
            db.session.rollback()
            return {"errors": [str(err)]}, 422

        return task.to_dict(), 200

    @login_required
    def delete(self, id, current_user):
        task = self._get_owned_task(id, current_user)
        if not task:
            return {"errors": ["Task not found"]}, 404

        db.session.delete(task)
        db.session.commit()
        return {}, 204
