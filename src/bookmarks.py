from flask import Blueprint, request, jsonify
import validators
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT
from src.database import Bookmark, db
from flask_jwt_extended import jwt_required, get_jwt_identity

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

# routes
# bookmarks route
@bookmarks.route("/", methods=['GET', 'POST'])
@jwt_required()
def handle_bookmarks():
    # get current user from token
    current_user = get_jwt_identity()
    
    # save the bookmark if method is post
    if request.method == 'POST':
        body = request.json.get('body', '')
        url = request.json.get('url', '')

        if not validators.url(url):
            return jsonify({
                "error": "URL in entered is not valid"
            }), HTTP_400_BAD_REQUEST
        
        if Bookmark.query.filter_by(url=url).first():
            return jsonify({
                "error": "The URL already exists in your bookmarks"
            }), HTTP_409_CONFLICT
        
        bookmark = Bookmark(body=body, url=url, user_id=current_user)
        db.session.add(bookmark)
        db.session.commit()

        return jsonify({
            "id": bookmark.id,
            "body": bookmark.body,
            "url": bookmark.url,
            "short_url": bookmark.short_url,
            "visits": bookmark.visits,
            "created_at": bookmark.created_at,
            "updated_at": bookmark.updated_at
        }), HTTP_201_CREATED
    
    else:
        bookmarks = Bookmark.query.filter_by(user_id=current_user)

        data = []

        for bookmark in bookmarks:
            data.append({
                "id": bookmark.id,
                "body": bookmark.body,
                "url": bookmark.url,
                "short_url": bookmark.short_url,
                "visits": bookmark.visits,
                "created_at": bookmark.created_at,
                "updated_at": bookmark.updated_at
            })

        return jsonify({
            "data": data
        }), HTTP_200_OK