from flask import Blueprint, request, jsonify, redirect
from src.database import User,db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token,jwt_required,create_refresh_token, get_jwt_identity
from flasgger import swag_from
import validators
from src.constants.http_status_codes import HTTP_200_OK,HTTP_201_CREATED,HTTP_401_UNAUTHORIZED,HTTP_409_CONFLICT,HTTP_400_BAD_REQUEST


auth = Blueprint('auth', __name__)

@auth.route('/api/v1/auth/signup', methods=['POST'])
@swag_from('./docs/auth/register.yml')
def create_user():
    username=request.json['username']
    email=request.json['email']
    password=request.json['password']
    pw_hash = generate_password_hash(password)

    if len(password)<6:
        return jsonify({'password':['Passwords should be at least 6 charatcers long']}), HTTP_400_BAD_REQUEST

    if len(username)<3:
        return jsonify({'username':['usernames should be at least 3 charatcers long']}),HTTP_400_BAD_REQUEST

    if not validators.email(email):
        return jsonify({'email':['Email is of invalid format']}),HTTP_400_BAD_REQUEST
    
    if not username.isalnum() or " " in username:
        return jsonify({'username':['username should only contain alphanumeric characters,no spaces']}),HTTP_400_BAD_REQUEST

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'email':['Email is taken']}),HTTP_409_CONFLICT

    if  User.query.filter_by(username=username).first() is not None:
        return jsonify({'username':['username is taken']}),HTTP_409_CONFLICT

    user=User(username=username, email=email,password=pw_hash)
    db.session.add(user)
    db.session.commit()


    return jsonify({'user':{
        'username':username,
        'email':email,
    }}),HTTP_201_CREATED


@auth.route('/api/v1/auth/login', methods=['POST'])
@swag_from('./docs/auth/login.yml')
def login():
    email=request.json.get('email','')
    password=request.json.get('password','')
    user=User.query.filter_by(email=email).first()

    if user:
        pass_correct=check_password_hash(user.password,password)
        if pass_correct:
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)

            return jsonify({'user':{
                'username':user.username,
                'email':user.email,
                'token':access_token,
                'refresh_token':refresh_token,
            }}),HTTP_200_OK

    return jsonify({
        'message':"Invalid credentials",
        
    }),HTTP_401_UNAUTHORIZED

@auth.route("/api/v1/auth/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
@swag_from('./docs/auth/refresh_token.yml')
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token}),HTTP_200_OK

