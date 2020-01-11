from app import db
from flask_login import UserMixin, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.zonainteres import ZonaInteres
from app.models.pathfotos import PathFotos
from app.models.estadisticas import Estadisticas

class User( db.Model, UserMixin ):
    id          = db.Column( db.Integer, primary_key = True )
    nombre      = db.Column( db.String )
    apellido    = db.Column( db.String )
    email       = db.Column( db.String )
    contrasena  = db.Column( db.String )

    eventos     = db.relationship('Evento' ,backref="user")         # ONE TO ONE
    zonas       = db.relationship('ZonaInteres' ,backref='user')    # ONE TO MANY

def CreateUser( nombre, apellido, email, password ):
    hash_pw = generate_password_hash( password, method="sha256" )
    new_user = User(
        nombre = nombre,
        apellido = apellido,
        email = email,
        contrasena = hash_pw
    )
    db.session.add( new_user )
    db.session.commit()
    print('[*] Usuario con email: {} creado correctamente.'.format(email))

def LoginUser( email, password ):
    user = User.query.filter_by( email = email ).first()
    if user is not None and check_password_hash( user.contrasena, password ):
        login_user( user )
        return True
    else:
        return False

def IndexData( cord ):
    current_zone = ZonaInteres.query.get( cord )
    if current_zone:
        path         = PathFotos.query.filter_by( owner = current_zone.id ).first()
        estadisticas = Estadisticas.query.filter_by( owner = path.id ).first()
        id           = current_zone.id
        url_1        = path.url_1
        url_2        = path.url_2

        areas     = [ estadisticas.area_00 ,estadisticas.area_25 ,estadisticas.area_50 ,estadisticas.area_75 ,estadisticas.area_100 ]
        percentil = [ estadisticas.p_05, estadisticas.p_25 ,estadisticas.p_50 ,estadisticas.p_75 ,estadisticas.p_95]

        coords        = [ [path.lan1, path.lng1] ,[path.lan2, path.lng2]]
        central_point = [ current_zone.lan, current_zone.lng ]
        fecha         = path.fecha
        area_25       = round(estadisticas.area_25, 2)
    else:
        url_1 = ""
        url_2 = ""
        coords = [[12, 12], [21,21]]
        central_point = [ 20, 20 ]
        fecha = ""
        estadisticas = ""
        area_25 = ""
        _id = ""
        areas = []
        percentil = []

    return url_1, url_2, coords, central_point, fecha, estadisticas, area_25, _id, areas, percentil
