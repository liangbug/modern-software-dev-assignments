from flask import Blueprint, jsonify, request

from app.db import get_db
from app.models import create_todo, delete_todo, get_todo, list_todos, update_todo

bp = Blueprint("todos", __name__, url_prefix="/api/todos")


@bp.get("")
def index():
    return jsonify(list_todos(get_db()))


@bp.post("")
def create():
    data = request.get_json(silent=True) or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    return jsonify(create_todo(get_db(), title)), 201


@bp.put("/<int:todo_id>")
def update(todo_id: int):
    data = request.get_json(silent=True) or {}

    title = data.get("title")
    if title is not None:
        title = title.strip()
        if not title:
            return jsonify({"error": "title cannot be empty"}), 400

    completed = data.get("completed")
    if completed is not None and not isinstance(completed, bool):
        return jsonify({"error": "completed must be a boolean"}), 400

    todo = update_todo(get_db(), todo_id, title, completed)
    if todo is None:
        return jsonify({"error": "todo not found"}), 404
    return jsonify(todo)


@bp.delete("/<int:todo_id>")
def delete(todo_id: int):
    if get_todo(get_db(), todo_id) is None:
        return jsonify({"error": "todo not found"}), 404
    delete_todo(get_db(), todo_id)
    return "", 204
