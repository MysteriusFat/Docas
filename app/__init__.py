from flask import *
from flask_admin import Admin
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_admin.contrib.sqla import ModelView
from werkzeug.security import generate_password_hash, check_password_hash

import ee

import os

app   = Flask( __name__ )
db    = SQLAlchemy( app )
ee.Initialize()


file_json = 'TestJS-9381bfacfaba.json'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath("database.db")
app.config['SECRET_KEY'] = 'dsakjdlajas'

from app import models

login = LoginManager( app )
admin = Admin( app )

class MyModelView( ModelView ):
    def is_accessible( self ):
        return current_user.is_authenticated

admin.add_view( MyModelView( models.Estadisticas, db.session ))
admin.add_view( MyModelView( models.PathFotos, db.session ))
admin.add_view( MyModelView( models.ZonaInteres, db.session ))
admin.add_view( MyModelView( models.User, db.session ))
admin.add_view( MyModelView( models.Evento, db.session ))

@login.user_loader
def load_user(user_id):
    return models.User.query.get(user_id)

from app import rutas
