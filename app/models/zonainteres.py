from app import db
from flask_login import UserMixin, current_user
from app.GeoShit.sentinel import Sentinel
from app.GeoShit.NASA_winner import geom_loading
from app.models.pathfotos import PathFotos
from app.models.estadisticas import Estadisticas

import json

class ZonaInteres( db.Model, UserMixin ):
    id      = db.Column( db.Integer, primary_key = True )
    nombre  = db.Column( db.String, unique = True )
    geojson = db.Column( db.String )
    lan     = db.Column( db.Float )
    lng     = db.Column( db.Float )

    paths   = db.relationship('PathFotos', backref='zonainteres')
    owner   = db.Column( db.Integer, db.ForeignKey('user.id'))

def CreateZone( nombre, file ):
    data = json.load( file )
    geom, x, y = geom_loading( data )
    new_zone = ZonaInteres(
        nombre  = nombre,
        geojson = str( data ),
        lan     = y,
        lng     = x,
        owner   = current_user.id
    )
    db.session.add( new_zone )
    db.session.commit()
    Sentinel( data , nombre, new_zone, geom )
