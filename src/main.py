from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from src.bookmarks.views import bookmarks
from src.authentication.views import auth
import os
from src.database.models import db
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow 
from flask_cors import CORS
from flasgger import APISpec, Schema, Swagger, fields

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}

template = {
  "swagger": "2.0",
  "info": {
    "title": "Bookmarks API",
    "description": "API for bookmarks",
    "contact": {
      "responsibleOrganization": "Cryce Truly",
      "responsibleDeveloper": "Cryce Truly",
      "email": "crycetruly@gmail.com",
      "url": "www.twitter.com/crycetruly",
    },
    "termsOfService": "www.twitter.com/crycetruly",
    "version": "1.0"
  },
  "host":"http://127.0.0.1:5000",
  "basePath": "/api/v1",  # base bash for blueprint registration
  "schemes": [
    "http",
    "https"
  ],
    "securityDefinitions": {
    "Bearer": {
      "type": "apiKey",
      "name": "Authorization",
      "in": "header",
      "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
    }
  },
}

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
app.config["JWT_SECRET_KEY"]=os.environ.get('JWT_SECRET_KEY')
app.config['SWAGGER'] = {
    'title': 'Bookmarks API',
    'uiversion': 3,
}

jwt = JWTManager(app)
CORS(app)


db.app = app
db.init_app(app)

swagger = Swagger(app, config=swagger_config,template=template)

app.register_blueprint(bookmarks)
app.register_blueprint(auth)





