from flask import Blueprint, request, jsonify
import validators
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
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
        # pagination parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 5, type=int)

        bookmarks = Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)

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

        meta = {
            "page": bookmarks.page,
            "pages": bookmarks.pages,
            "total_count": bookmarks.total,
            "next_page": bookmarks.next_num,
            "prev_page": bookmarks.prev_num,
            "has_next": bookmarks.has_next,
            "has_prev": bookmarks.has_prev
        }

        return jsonify({
            "data": data,
            "meta": meta
        }), HTTP_200_OK

# get on bookmark by id
@bookmarks.get("/<int:id>")
@jwt_required()
def get_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()
    
    if not bookmark:
        return jsonify({
            "message": "Bookmark not found."
        }), HTTP_404_NOT_FOUND

    return jsonify({
        "id": bookmark.id,
        "body": bookmark.body,
        "url": bookmark.url,
        "short_url": bookmark.short_url,
        "visits": bookmark.visits,
        "created_at": bookmark.created_at,
        "updated_at": bookmark.updated_at
    }), HTTP_200_OK


# route to edit bookmark
@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user)

    # check if exists
    if not bookmark:
        return jsonify({
            "error": "Bookmark not found"
        }), HTTP_404_NOT_FOUND
    
    body = request.json.get('body', '')
    url = request.json.get('url', '')

    # set the new bookmark values
    bookmark.body = body
    bookmark.url = url

    db.session.commit()

    # return editted bookmark
    return jsonify({
        "bookmark": bookmark
    }), HTTP_200_OK


# delete bookmark route
