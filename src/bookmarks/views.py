from flask import Blueprint, request, jsonify, redirect, render_template
from flask_cors import CORS
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from src.database.models import Bookmark,User,db
import validators
from flasgger import swag_from


bookmarks = Blueprint('bookmarks', __name__)


@bookmarks.route('/api/v1/bookmarks/', methods=['POST','GET'])
@jwt_required()
@swag_from('../docs/bookmarks/get_all.yml')
def get_all_bookmarks():

    current_user=get_jwt_identity()

    if request.method=='GET':
        data=[]
        bookmarks=Bookmark.query.filter_by(user_id=current_user).all()

        for x in bookmarks:
            data.append({
                'id':x.id,
                'url':x.url,
                'body':x.body,
                'created_at':x.created_at,
                'updated_at':x.updated_at,
            })
        return jsonify(data),200

    body=request.get_json().get('body','')
    url=request.get_json().get('url','')

    if not validators.url(url):
        return jsonify({'url':'No valid url'}),400

    bookmark=Bookmark(url=url,body=body,user_id=current_user)
    db.session.add(bookmark)
    db.session.commit()

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'body':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at,
    }),201



@bookmarks.route('/api/v1/bookmarks/<int:id>', methods=['GET'])
@jwt_required()
@swag_from('../docs/bookmarks/get_one.yml')
def get_bookmark(id):
    current_user=get_jwt_identity()
    bookmark=Bookmark.query.filter_by(id=id,user_id=current_user).first()

    if bookmark is None:
        return jsonify({'item':"Not found"}),404

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'body':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at,
    }),200




@bookmarks.route('/api/v1/bookmarks/<int:id>', methods=['DELETE'])
@jwt_required()
@swag_from('../docs/bookmarks/delete_one.yml')
def delete_bookmark(id):
    current_user=get_jwt_identity()
    bookmark=Bookmark.query.filter_by(id=id,user_id=current_user).first()
    if bookmark is None:
        return jsonify({'item':"Not found"}),404

    db.session.delete(bookmark)
    db.session.commit()
    return jsonify({}),204


@bookmarks.route('/api/v1/bookmarks/<int:id>', methods=['PUT','PATCH'])
@jwt_required()
@swag_from('../docs/bookmarks/edit_one.yml')
def edit_bookmark(id):
    current_user=get_jwt_identity()
    bookmark=Bookmark.query.filter_by(id=id,user_id=current_user).first()

    if bookmark is None:
        return jsonify({'item':"Not found"}),404
    
    body=request.get_json().get('body','')
    url=request.get_json().get('url','')

    if not validators.url(url):
        return jsonify({'url':'No valid url'}),400

    bookmark.url=url
    bookmark.body=body
    db.session.commit()

    return jsonify({
        'id':bookmark.id,
        'url':bookmark.url,
        'body':bookmark.body,
        'created_at':bookmark.created_at,
        'updated_at':bookmark.updated_at,
    }),200
