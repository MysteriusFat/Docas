from app import db
from flask_login import UserMixin
from app.models.subs import subs
from flask_login import current_user

class Evento( db.Model, UserMixin ):
    id          = db.Column( db.Integer ,primary_key = True )
    nombre      = db.Column( db.String )
    fecha       = db.Column( db.DateTime )
    ubicacion   = db.Column( db.String )
    descripcion = db.Column( db.String )

    organizador   = db.Column( db.Integer ,db.ForeignKey('user.id'))
    participantes = db.relationship('User' ,secondary=subs ,lazy='subquery' ,backref = db.backref('participantes', lazy=True))

def CreateEvent( nombre, ubicacion, descripcion ):
    new_event = Evento(
        nombre      = nombre,
        fecha       = datetime.strptime(request.form['fecha'], '%Y-%m-%d'),
        ubicacion   = ubicacion,
        descripcion = descripcion,
        organizador = current_user.id
    )
    db.session.add( new_event )
    db.session.commit()
