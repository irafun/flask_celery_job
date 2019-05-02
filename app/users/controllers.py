# Flask
from flask import request
from flask_restful import Resource
from werkzeug.security import safe_str_cmp
from flask_jwt_extended import create_access_token

# 3rd party
from marshmallow import ValidationError

# local
from .models import *
from .serializers import *

USER_EXISTS = "user with username='{}' already exists"
INVALID_CREDENTIALS = "Invalid credentials!"

user_serializer = UserSerializer()
user_list_serializer = UserSerializer(many=True)

class UserRegister(Resource):
    def post(self):
        data = request.get_json()
        try:
            user = user_serializer.load(data)
        except ValidationError as err:
            return err.messages, 400

        if UserModel.find_by_username(user.username):
            return({'message': USER_EXISTS.format(user.username)}), 400

        user.save_to_db()

        return user_serializer.dump(data), 201

    def get(self):
        return {'results': user_list_serializer.dump(UserModel.find_all())}

class UserLogin(Resource):
    @classmethod
    def post(cls):
        try:
            data = request.get_json()
            user_data = user_serializer.load(data)
        except ValidationError as err:
            return err.messages, 400

        user = UserModel.find_by_username(user_data.username)

        if user and safe_str_cmp(user.password, user_data.password):
            access_token = create_access_token(identity=user.id, fresh=True)
            return {"access_token": access_token}, 200
        return {"message": INVALID_CREDENTIALS}, 401