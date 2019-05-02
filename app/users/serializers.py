# local
from utils import *
from .models import UserModel

class UserSerializer(ma.ModelSchema):
    class Meta:
        model = UserModel
        load_only = ("password",)
        dump_only = ("id",)