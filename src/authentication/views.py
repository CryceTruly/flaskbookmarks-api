from flask import Blueprint, request, jsonify, redirect, current_app
from src.database.models import User,db
from werkzeug.security import generate_password_hash, check_password_hash
from validate_email import validate_email
from flask_jwt_extended import create_access_token,jwt_required,create_refresh_token, get_jwt_identity
from flasgger import swag_from


auth = Blueprint('auth', __name__)

@auth.route('/api/v1/auth/signup', methods=['POST'])
@swag_from('../docs/auth/register.yml')
def create_user():

    username=request.json['username']
    email=request.json['email']
    password=request.json['password']
    pw_hash = generate_password_hash(password)

    if len(password)<6:
        return jsonify({'password':['Passwords should be at least 6 charatcers long']}), 400

    if len(username)<3:
        return jsonify({'username':['usernames should be at least 3 charatcers long']}),400

    if not validate_email(email):
        return jsonify({'email':['Email is of invalid format']}),400
    
    if not username.isalnum() or " " in username:
        return jsonify({'username':['username should only contain alphanumeric characters,no spaces']}),400

    if User.query.filter_by(email=email).first() is not None:
        return jsonify({'email':['Email is taken']}),409

    if  User.query.filter_by(username=username).first() is not None:
        return jsonify({'username':['username is taken']}),409

    user=User(username=username, email=email,password=pw_hash)
    db.session.add(user)
    db.session.commit()


    return jsonify({'user':{
        'username':username,
        'email':email,
    }}),201


@auth.route('/api/v1/auth/login', methods=['POST'])
@swag_from('../docs/auth/login.yml')
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
            }}),200

    return jsonify({
        'message':"Invalid credentials",
        
    }),401

@auth.route("/api/v1/auth/token/refresh", methods=["POST"])
@jwt_required(refresh=True)
@swag_from('../docs/auth/refresh_token.yml')
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify({'access_token': access_token})
