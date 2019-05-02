# python
from datetime import datetime
import requests

# local
from utils import *

MAILGUN_DOMAIN_NAME = "sandbox2f2a2e3145db4a4887d37ae33ea2af15.mailgun.org"
MAILGUN_API_KEY = "9065ae36638c7734500ef2be193433d7-7bce17e5-47e83106"

class EmailModel(db.Model):
    __tablename__ = 'schedulers'

    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, unique=True, nullable=False)
    email_to = db.Column(db.String(128), nullable=False)
    email_subject = db.Column(db.String(128), nullable=False)
    email_content = db.Column(db.Unicode(length=2048), nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    sent = db.Column(db.Boolean, default=False)

    @classmethod
    def find_all(cls):
        return cls.query.all()

    @classmethod
    def find_by_id(cls, event_id):
        return cls.query.filter_by(event_id=event_id).first()

    @classmethod
    def check_sent(cls):
        return cls.query.filter_by(sent=True)

    @classmethod
    def check_unsent(cls):
        return cls.query.filter_by(sent=False)

    @classmethod
    def check_not_sent(cls, event_id):
        return cls.query.filter_by(event_id=event_id, sent=False).first()

    def save_to_db(self):
        # self.timestamp = datetime.strptime(self.timestamp, '%d %b %Y %H:%M')
        db.session.add(self)
        db.session.commit()

    def delete_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def email_send(self):
        url = 'https://api.mailgun.net/v3/{}/messages'.format(MAILGUN_DOMAIN_NAME)
        auth = ('api', MAILGUN_API_KEY)
        data = {
            'from': 'Mailgun User <mailgun@{}>'.format(MAILGUN_DOMAIN_NAME),
            'to': self.email_to,
            'subject': self.email_subject,
            'text': self.email_content,
        }

        response = requests.post(url, auth=auth, data=data)
        response.raise_for_status()
