# Flask
from flask import request
from flask_restful import Resource
from flask_jwt_extended import jwt_required # JSON token

# 3rd party
from marshmallow import ValidationError

# python
from datetime import datetime

# local
from .models import *
from .serializers import *

# errors messages
ENTITY_EXISTS = "The data you entered already exists"
EVENT_ID_NOT_UNIQUE = "The data with event_id='{}' already exists"
INSERTING_ERROR = "An error occurred inserting the instance"
UPDATING_ERROR = "An error occurred updating the instance"
DELETING_ERROR = "An error occurred deleting the instance"
DELETING_SUCCESS = "Item deleted"
NOT_FOUND = "Item not found"
CELERY_JOB_QUEUED = "{} Celery job queued"
NO_MORE_UNSENT = "no unsent emails remaining"
ALREADY_SENT = "email with event_id='{}' already been sent"
ERROR_SENDING = "there is a problem in sending the email, please try again later"

email_serializer = EmailSerializer()
email_list_serializer = EmailSerializer(many=True)

class GetPostEmail(Resource):
    def get(self):
        return {'results': email_list_serializer.dump(EmailModel.find_all())}

    def post(self):
        data = request.get_json()
        try:
            save_email = email_serializer.load(data)
        except ValidationError as err:
            return err.messages, 400

        check_by_id = save_email.find_by_id(save_email.event_id)
        if check_by_id:
            return({'message': EVENT_ID_NOT_UNIQUE.format(save_email.event_id)}), 409
        if check:
            return({'message': ENTITY_EXISTS}), 409

        try:
            save_email.save_to_db()
            return email_serializer.dump(EmailModel.find_by_id(save_email.event_id)), 201
        except:
            return({'message': INSERTING_ERROR}), 500
        

class RetrieveUpdateDeleteEmail(Resource):
    def get(self, event_id):
        result = EmailModel.find_by_id(event_id)
        if result:
            return email_serializer.dump(result)
        return({'message': NOT_FOUND}), 404

    @jwt_required
    def put(self, event_id):
        save_email = EmailModel.find_by_id(event_id)
        if not save_email:
            return({'message': NOT_FOUND}), 404

        data = request.get_json()
        
        email_to = data.get('email_to')
        if email_to:
            save_email.email_to = email_to

        email_subject = data.get('email_subject')
        if email_subject:
            save_email.email_subject = email_subject
            
        email_content = data.get('email_content')
        if email_content:
            save_email.email_content = email_content
        
        timestamp = data.get('timestamp')
        if timestamp:
            save_email.timestamp = timestamp

        try:
            save_email.save_to_db()
            return email_serializer.dump(save_email.find_by_id(event_id))
        except:
            return({'message': UPDATING_ERROR}), 500

    @jwt_required
    def delete(self, event_id):
        save_email = EmailModel.find_by_id(event_id)
        if save_email is None:
            return({'message': NOT_FOUND}), 404
        try:
            save_email.delete_from_db()
            return({'message': DELETING_SUCCESS})
        except:
            return({'message': DELETING_ERROR}), 500
        return({'message': NOT_FOUND}), 404

class CheckSentEmail(Resource):
    def get(self):
        return({'results': email_list_serializer.dump(EmailModel.check_sent())})

class CheckUnsentEmail(Resource):
    def get(self):
        return({'results': email_list_serializer.dump(EmailModel.check_unsent())})
