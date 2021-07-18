import os
from flask import Flask,redirect,jsonify
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flasgger import  Swagger,swag_from
from src.bookmarks import bookmarks
from src.authentication import auth
from config.swagger import swagger_config,template
from src.database import db,Bookmark
from src.constants.http_status_codes import HTTP_500_INTERNAL_SERVER_ERROR,HTTP_404_NOT_FOUND

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        app.config.from_mapping(
        SECRET_KEY='dev',
        SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        JWT_SECRET_KEY=os.environ.get('JWT_SECRET_KEY'),
        SWAGGER = {
        'title': 'Bookmarks API',
        'uiversion': 3,
            }   
    )
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)


    JWTManager(app)
    CORS(app)
    
    db.app = app
    db.init_app(app)

    Swagger(app, config=swagger_config,template=template)

    app.register_blueprint(bookmarks)
    app.register_blueprint(auth)

    @app.route('/<short_url>')
    @swag_from('./docs/bookmarks/redirect.yml')
    def redirect_to_url(short_url):
        link = Bookmark.query.filter_by(short_url=short_url).first_or_404()
        link.visits = link.visits + 1
        db.session.commit()
        return redirect(link.url)

    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({"Error": 'not found'}), HTTP_404_NOT_FOUND

    @app.errorhandler(500)
    def page_not_found(e):
        return jsonify({"Error": 'Issue on server occurred'}), HTTP_500_INTERNAL_SERVER_ERROR

    return app
