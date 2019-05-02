# local
from utils import *
from .models import EmailModel

class EmailSerializer(ma.ModelSchema):
    class Meta:
        model = EmailModel
        dump_only = ("id","sent")