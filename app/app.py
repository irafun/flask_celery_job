# Flask
from flask import Flask
from flask_restful import Api, Resource
from flask_jwt import JWT # JSON token
from flask_jwt_extended import JWTManager

# 3rd party
from datetime import datetime
from pytz import timezone

# local
from security import authenticate, identity
from users.controllers import *
from emails.controllers import *
from utils import * # includes flask_marshmallow, flask_sqlalchemy, celery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///jublia.db' # using sqlite for simplicity
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # using basic SQLAlchemy tracker for simplicity
app.config['CELERY_BROKER_URL'] = 'amqp://localhost//'
app.config['CELERY_BACKEND'] = 'db+sqlite:///celery.sqlite'
app.secret_key = "ShuSh! iT's a SecreT"

api = Api(app)
celery = make_celery(app)

@app.before_first_request
def create_tables():
    db.create_all()

jwt = JWTManager(app)

@celery.task(name='tasks.uppering')
def uppering(word):
    return word.upper()

@celery.task(name='tasks.send_email')
def send_email(obj):
    return obj.email_send()

class SendEmail(Resource):
    def get(self, event_id):
        obj = EmailModel.check_not_sent(event_id)
        if obj:
            when = timezone('Asia/Singapore').localize(obj.timestamp)
            send_email.apply_async((obj,), eta=when)
            
            if send_email.apply_async((obj,), eta=when):
                obj.sent = True # to indicate the email has been sent
                try:
                    obj.save_to_db()
                except:
                    return({'message': UPDATING_ERROR}), 500

                return({'message': CELERY_JOB_QUEUED.format('1')})
            return({'message': ERROR_SENDING})
        return({'message': ALREADY_SENT.format(event_id)}), 404

class SendUnsentEmail(Resource):
    def get(self):
        results = EmailModel.check_unsent()

        if results:
            num = 0
            for obj in results:
                when = timezone('Asia/Singapore').localize(obj.timestamp)
                send_email.apply_async((obj,), eta=when)
                if send_email.apply_async((obj,), eta=when):
                    obj.sent = True
                    num += 1
                    try:
                        obj.save_to_db()
                    except:
                        return({'message': UPDATING_ERROR}), 500
                else:
                    return({'message': ERROR_SENDING})
            return({'message': CELERY_JOB_QUEUED.format(num)})
        return({'message': NO_MORE_UNSENT}), 404

# ===== This class is for automatically assigning new celery job when the instance is created ===== #
class PostEmailAutoCelery(Resource):
    def post(self):
        data = request.get_json()
        try:
            save_email = email_serializer.load(data)
        except ValidationError as err:
            return err.messages, 400

        check_by_id = save_email.find_by_id(save_email.event_id)
        if check_by_id:
            return({'message': EVENT_ID_NOT_UNIQUE.format(save_email.event_id)})
        try:
            save_email.save_to_db()
        except:
            return({'message': INSERTING_ERROR}), 500

        when = timezone('Asia/Singapore').localize(save_email.timestamp)
        send_email.apply_async((save_email,), eta=when)
        if send_email.apply_async((save_email,), eta=when):
            save_email.sent = True
            save_email.save_to_db()
            
        return email_serializer.dump(EmailModel.find_by_id(save_email.event_id)), 201
        

api.add_resource(UserRegister, '/users')
api.add_resource(UserLogin, '/users/login')
api.add_resource(GetPostEmail, '/save_emails/nonauto')
api.add_resource(CheckSentEmail, '/save_emails/sent') # checking which email(s) has been sent
api.add_resource(CheckUnsentEmail, '/save_emails/unsent') # checking which email(s) has not been sent
api.add_resource(SendUnsentEmail, '/save_emails/unsent/sendall') # sending all the email(s) that has not been sent
api.add_resource(RetrieveUpdateDeleteEmail, '/save_emails/<int:event_id>/')

api.add_resource(SendEmail, '/save_emails/<int:event_id>/send') # endpoint for queueing the spesific instance
api.add_resource(PostEmailAutoCelery, '/save_emails') # endpoint for auto queueing the object just created

if __name__ == '__main__':
    from utils import *
    db.init_app(app)
    ma.init_app(app)
    app.run(port=5000, debug=True)