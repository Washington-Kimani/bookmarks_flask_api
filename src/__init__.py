from flask import Flask, redirect, request
from flask_cors import CORS
import os
from src.auth import auth
from src.bookmarks import bookmarks
from src.users import users
from src.database import db, Bookmark
from flask_jwt_extended import JWTManager
from flasgger import Swagger, swag_from
from src.config.swagger import swagger_config, template

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    CORS(app, resources={r"/api/v1/*": {"origins": ["http://localhost:3000", "http://localhost:3001", "https://bookmark-manager-codes.vercel.app"]}})

    @app.before_request
    def check_for_options():
        if request.method == "OPTIONS":
            return "", 200
        return None

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
    app.register_blueprint(users)

    Swagger(app, template=template)

    # handle short url redirect
    @app.get('/<short_url>')
    @swag_from('./docs/short_url.yaml')
    def redirect_to_url(short_url):
        bookmark = Bookmark.query.filter_by(short_url=short_url).first_or_404()

        if bookmark:
            bookmark.visits = bookmark.visits+1
            db.session.commit()

            return redirect(bookmark.url)


    if __name__ == "__main__":
        app.run(debug=True, use_reloader=False)


    return app