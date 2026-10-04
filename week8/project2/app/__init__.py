from pathlib import Path

from flask import Flask

from app.db import close_db, init_db


def create_app(db_path: str | None = None) -> Flask:
    project_root = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(project_root / "templates"),
        static_folder=str(project_root / "static"),
    )

    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    app.config["DATABASE"] = db_path or str(data_dir / "todos.db")

    with app.app_context():
        init_db(app.config["DATABASE"])

    app.teardown_appcontext(close_db)

    from app.routes import bp as todos_bp

    app.register_blueprint(todos_bp)

    @app.get("/")
    def index():
        from flask import render_template

        return render_template("index.html")

    return app
