from flask import Flask
from app.tasks.routes import tasks_bp
from app.extensions.db import db
from app.errors.handlers import register_error_handlers

def create_app(testing: bool = False):
    app = Flask(__name__)

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        "sqlite:///:memory:" if testing else "sqlite:///tasks.db"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    with app.app_context():
        db.create_all()

    app.register_blueprint(tasks_bp)
    register_error_handlers(app)

    return app
