from flask import Blueprint, request, jsonify
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from src.database import Bookmark,db
import validators
from flasgger import swag_from
from src.constants.http_status_codes import HTTP_200_OK,HTTP_201_CREATED,HTTP_204_NO_CONTENT,HTTP_400_BAD_REQUEST,HTTP_404_NOT_FOUND

bookmarks = Blueprint('bookmarks', __name__,url_prefix="/api/v1")

@bookmarks.route('/bookmarks/', methods=['POST','GET'])
@jwt_required()
@swag_from('./docs/bookmarks/get_all.yml')
def get_all_bookmarks():

    current_user=get_jwt_identity()

    if request.method=='GET':
        page = request.args.get('page', 1, type=int)
        per_page= request.args.get('per_page', 1, type=int)
        data=[]
        bookmarks=Bookmark.query.filter_by(user_id=current_user).paginate(page=page, per_page=per_page)
        print(bookmarks)
        for bookmark in bookmarks.items:
            data.append({
                'id':bookmark.id,
                'url':bookmark.url,
                'visits':bookmark.visits,
                'short_url':request.url_root+bookmark.short_url,
                'body':bookmark.body,
                'created_at':bookmark.created_at,
                'updated_at':bookmark.updated_at,

            })
        meta={'has_next':bookmarks.has_next,
            'has_prev':bookmarks.has_prev,
            'next_num':bookmarks.next_num,
            'page':bookmarks.page,
            'pages':bookmarks.pages,
            'prev_num':bookmarks.prev_num,
            'total':bookmarks.total
        }
        return jsonify({'results':data,'meta':meta}),HTTP_200_OK

    body=request.get_json().get('body','')
    url=request.get_json().get('url','')

    if not validators.url(url):
        return jsonify({'url':'No valid url'}),HTTP_400_BAD_REQUEST

    link = Bookmark.query.filter_by(url=url).first()
    if link:
        return jsonify({"url": ["Already  exists"]}), HTTP_400_BAD_REQUEST

    bookmark=Bookmark(url=url,body=body,user_id=current_user)
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'short_url':request.url_root+bookmark.short_url,
        'visits':bookmark.visits,
        'body':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at,
    }),HTTP_201_CREATED



@bookmarks.route('/bookmarks/<int:id>', methods=['GET'])
@jwt_required()
@swag_from('./docs/bookmarks/get_one.yml')
def get_bookmark(id):
    current_user=get_jwt_identity()
    bookmark=Bookmark.query.filter_by(id=id,user_id=current_user).first()

    if bookmark is None:
        return jsonify({'item':"Not found"}),HTTP_404_NOT_FOUND

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'short_url':request.url_root+bookmark.short_url,
         'visits':bookmark.visits,
        'body':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at,
    }),HTTP_200_OK




@bookmarks.route('/bookmarks/<int:id>', methods=['DELETE'])
@jwt_required()
@swag_from('./docs/bookmarks/delete_one.yml')
def delete_bookmark(id):
    current_user=get_jwt_identity()
    bookmark=Bookmark.query.filter_by(id=id,user_id=current_user).first()
    if bookmark is None:
        return jsonify({'item':"Not found"}),HTTP_404_NOT_FOUND

    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({}),HTTP_204_NO_CONTENT


@bookmarks.route('/bookmarks/<int:id>', methods=['PUT','PATCH'])
@jwt_required()
@swag_from('./docs/bookmarks/edit_one.yml')
def edit_bookmark(id):
    current_user=get_jwt_identity()
    bookmark=Bookmark.query.filter_by(id=id,user_id=current_user).first()

    if bookmark is None:
        return jsonify({'item':"Not found"}),HTTP_404_NOT_FOUND
    
    body=request.get_json().get('body','')
    url=request.get_json().get('url','')

    if not validators.url(url):
        return jsonify({'url':'No valid url'}),HTTP_400_BAD_REQUEST

    bookmark.url=url
    bookmark.body=body
    db.session.commit()

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'body':bookmark.body,
        'short_url':request.url_root+bookmark.short_url,
         'visits':bookmark.visits,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at,
    }),HTTP_200_OK



@bookmarks.route('/bookmarks/stats')
@jwt_required()
@swag_from('./docs/bookmarks/stats.yml')
def stats():
    current_user=get_jwt_identity()
    items = Bookmark.query.filter_by(user_id=current_user).all()
    json_data = []
    for link in items:
        newLink = {"visits": link.visits,
                   "url": link.url, "short": request.url_root+link.short_url, "id": link.id}
        json_data.append(newLink)

    return jsonify({"stats": json_data}),HTTP_200_OK
