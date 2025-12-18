from flask import Blueprint, request, jsonify
import validators
from src.constants.http_status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_204_NO_CONTENT, HTTP_206_PARTIAL_CONTENT, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_409_CONFLICT
from src.database import Bookmark, db
from flask_jwt_extended import jwt_required, get_jwt_identity

from src.utils.get_favicon import fetch_favicon

bookmarks = Blueprint("bookmarks", __name__, url_prefix="/api/v1/bookmarks")

# routes
# bookmarks get route
@bookmarks.get("/")
@jwt_required()
def handle_bookmarks():
    # get current user from token
    current_user = get_jwt_identity()

    # pagination parameters
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)

    bookmarks = Bookmark.query.filter_by(user_id=current_user,archived=False).paginate(page=page, per_page=per_page)

    data = []

    for bookmark in bookmarks:
        data.append({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'icon_url': bookmark.icon_url,
            'description': bookmark.description,
            'archived': bookmark.archived,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at,
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

# create a new bookmark
@bookmarks.post("/")
@jwt_required()
def handle_create_bookmark():
    current_user = get_jwt_identity()
    # save the bookmark
    body = request.json.get('body', '')
    url = request.json.get('url', '')
    description = request.json.get('description', '')

    icon_url = fetch_favicon(url)

    if not validators.url(url):
        return jsonify({
            "error": "URL in entered is not valid"
        }), HTTP_400_BAD_REQUEST

    if Bookmark.query.filter_by(url=url).first():
        return jsonify({
            "error": "The URL already exists in your bookmarks"
        }), HTTP_409_CONFLICT

    bookmark = Bookmark(body=body, url=url, description=description, icon_url=icon_url, user_id=current_user)
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({
        "data": {
            'id': bookmark.id,
            'body': bookmark.body,
            'description': bookmark.description,
            'url': bookmark.url,
            'icon_url': bookmark.icon_url,
            'short_url': bookmark.short_url,
            'visits': bookmark.visits,
            'archived': bookmark.archived,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at
        }
    }), HTTP_201_CREATED

# get one bookmark by id
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
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'icon_url': bookmark.icon_url,
        'description': bookmark.description,
        'archived': bookmark.archived,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK


# route to edit bookmark
@bookmarks.put("/<int:id>")
@bookmarks.patch("/<int:id>")
@jwt_required()
def edit_bookmark(id):
    current_user = get_jwt_identity()
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()

    # check if exists
    if not bookmark:
        return jsonify({
            "error": "Bookmark not found"
        }), HTTP_404_NOT_FOUND
    
    body = request.json.get('body', '')
    url = request.json.get('url', '')
    description = request.json.get('description', '')

    if not validators.url(url):
        return jsonify({
            'error': 'Enter a valid url'
        }), HTTP_400_BAD_REQUEST

    bookmark.url = url
    bookmark.body = body
    bookmark.description = description

    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'icon_url': bookmark.icon_url,
        'description': bookmark.description,
        'archived': bookmark.archived,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK

# archive a bookmark
@bookmarks.put("/<int:id>/archive")
@jwt_required()
def archive_bookmark(id):
    if not id:
        return jsonify({
            "message": "Bookmark ID is required to archive a bookmark."
        }), HTTP_206_PARTIAL_CONTENT
    # get user ID
    current_user = get_jwt_identity()
    # get the bookmark
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()

    if not bookmark:
        return jsonify({
            "message": "Bookmark not found"
        }), HTTP_404_NOT_FOUND

    archived = request.json.get('archived')

    if archived is None:
       return jsonify({
           "error": "`archived` boolean is required.",
       }), HTTP_400_BAD_REQUEST

    bookmark.archived = bool(archived)
    db.session.commit()

    return jsonify({
        'id': bookmark.id,
        'url': bookmark.url,
        'short_url': bookmark.short_url,
        'visit': bookmark.visits,
        'body': bookmark.body,
        'icon_url': bookmark.icon_url,
        'description': bookmark.description,
        'archived': bookmark.archived,
        'created_at': bookmark.created_at,
        'updated_at': bookmark.updated_at,
    }), HTTP_200_OK

# get archived bookmarks
@bookmarks.get("/archived")
@jwt_required()
def get_archived_bookmarks():
    current_user = get_jwt_identity()
    # get the bookmarks
    bookmarks = Bookmark.query.filter_by(archived=True, user_id=current_user).all()
    print(bookmarks)

    data = []

    for bookmark in bookmarks:
        data.append({
            'id': bookmark.id,
            'url': bookmark.url,
            'short_url': bookmark.short_url,
            'visit': bookmark.visits,
            'body': bookmark.body,
            'icon_url': bookmark.icon_url,
            'description': bookmark.description,
            'archived': bookmark.archived,
            'created_at': bookmark.created_at,
            'updated_at': bookmark.updated_at,
        })

    return jsonify({
        'data': data,
    })


# delete bookmark route
@bookmarks.delete("/<int:id>")
@jwt_required()
def delete_bookmark(id):
    if not id:
        return ({
            "message": "Bookmark ID is required for this operation"
        }), HTTP_206_PARTIAL_CONTENT
    # get uer id
    current_user = get_jwt_identity()
    # get the bookmark
    bookmark = Bookmark.query.filter_by(id=id, user_id=current_user).first()

    if not bookmark:
        return jsonify({
            "message": "The bookmark was not found"
        }), HTTP_404_NOT_FOUND
    
    db.session.delete(bookmark)
    db.session.commit()

    return jsonify({}), HTTP_204_NO_CONTENT


# get link visits stats
@bookmarks.get('/stats')
@jwt_required()
def get_stats():
    current_user = get_jwt_identity()

    data = []

    # get all links
    links = Bookmark.query.filter_by(user_id=current_user).all()

    for link in links:
        new_link  = {
            'id': link.id,
            'visits': link.visits,
            'url': link.url,
            'short_url': link.short_url
        }

        data.append(new_link)

    return jsonify({"data":data}), HTTP_200_OK