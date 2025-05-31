from flask import Flask
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.database import db
from flask_jwt_extended import JWTManager

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    if test_config is None:
        db_uri = os.getenv("SQLALCHEMY_DB_URI")
        if not db_uri:
            raise RuntimeError("SQLALCHEMY_DB_URI environment variable is not set")
        
        app.config.from_mapping(
            SECRET_KEY=os.getenv('SECRET_KEY'),
            SQLALCHEMY_DATABASE_URI=db_uri,
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JWT_SECRET_KEY=os.getenv('JWT_SECRET_KEY')
        )
    else:
        app.config.from_mapping(test_config)

    db.init_app(app)

    JWTManager(app)

    app.register_blueprint(auth)
    app.register_blueprint(bookmarks)


    if __name__ == "__main__":
        app.run(debug=True, use_reloader=False)


    return app